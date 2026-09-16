#!/usr/bin/env python3
"""
리뷰 스토어 동기화 — 단일 스토어(data/reviews.json), id 로 중복 제거.

**왜 단일 스토어인가**

알파리뷰는 리뷰를 상품별로 분리해 주지 않는다. 성분이 같은 상품군이 같은 리뷰 풀을
공유한다(실측: `magnesium` = `daypack-magnesium` = `set-performance` 가 표본 60건
전수 일치, 보유 건수도 모두 18,799. `set-swell` 33,631 ≈ 칼륨 26,970 + 비타민B 6,484).

그래서 `product_no=64` 로 조회해도 실제로는 `product_no=16` 리뷰가 섞여 나온다.
조회에 쓴 product_no 로 페이지를 나누면 마그네슘 리뷰가 '퍼포먼스 세트' 후기로도
게재되어 **중복 콘텐츠이고 사실과도 다르다.**

다행히 API 는 리뷰마다 진짜 소속 상품을 알려준다(`product.product_no` / `product_name`).
그래서 전 상품을 한 스토어에 모아 id 로 중복을 제거하고, **빌더가 리뷰 자신의
product_no 로 페이지를 나눈다.** 어떤 리뷰도 두 번 게재되지 않는다.

입력 두 가지:
  1) 위젯 API   — 신규 리뷰. `--api` 는 페이지 예산 안에서만 걷는다
  2) 엑셀 CSV   — 과거 이력 백필(1회). API 는 상품당 약 1,497건에서 막힌다

사용:
  python3 _sync.py --api            신규만 (매일 · 워크플로가 이걸 돈다)
  python3 _sync.py --deep 11        특정 product_no 전 구간 (중단되면 재실행으로 이어짐)
  python3 _sync.py --csv export.csv 엑셀 백필
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
STORE = os.path.join(DATA, "reviews.json")

BASE = "https://review-widget.alphwidget.com/v2/api-widget"
MALL, SHOP, WIDGET = "wespotjo", "1", "7ee3b8bd"
HDRS = {"Referer": "https://zengenetics.co.kr/", "Origin": "https://zengenetics.co.kr",
        "Accept": "application/json", "User-Agent": "zengenetics-review-sync/1.0"}

PAGE_CLAMP = 499          # page 500 이후는 같은 3건이 반복된다 (이진탐색 확인)
MISS_TOLERANCE = 3        # 아래 '고정 노출 리뷰' 주석 참고
MAX_PAGES_INCREMENTAL = 20

# 위젯의 기본 정렬은 순수 최신순이 아니다. 앞머리에 **고정 노출 리뷰 4건**이 붙고
# (page 1 전체 + page 2 첫 항목) 그 뒤부터 id 내림차순(최신순)이 시작된다.
#   page 1 → 78633090, 75141298, 74012666
#   page 2 → 68037045, 99940570, 99919641   ← 여기서 최신순이 시작
# 그래서 "아는 id 를 만나면 중단"은 틀렸다. 고정 리뷰만 있는 page 1 에서 멈춰 신규를
# 영구히 놓친다. 신규 없는 페이지가 MISS_TOLERANCE 번 연속일 때만 멈춘다.
#
# 증분 모드에 페이지 예산을 두는 이유: 스토어가 비어 있으면 아는 id 가 없어
# MISS_TOLERANCE 에 영원히 도달하지 않고 PAGE_CLAMP 까지 걷는다. 상품 10종이면 매일
# 5,000 요청이 되어 벤더 API 를 과하게 두드린다. 과거 이력은 --deep / --csv 의 일이다.

# 이관된 네이버페이 구매평은 본문 끝에 실제 작성일이 박혀 있다.
#   "잘받았습니다.좋아요.,(2025-09-19 17:40:31 에 등록된 네이버 페이 구매평)"
# API 응답에 작성일 필드가 없으므로 이게 유일한 실제 날짜 출처다 (약 13%).
EMBEDDED_DATE = re.compile(r"\((\d{4}-\d{2}-\d{2})[^)]*에 등록된[^)]*\)")


def products():
    return json.load(open(os.path.join(DATA, "products.json"), encoding="utf-8"))


def api(path="", tries=4, **q):
    """연결 리셋이 흔하다 — 지수 백오프로 재시도한다."""
    url = f"{BASE}{path}?" + urllib.parse.urlencode(
        {"mall_id": MALL, "shop_no": SHOP, "widget_code": WIDGET, **q})
    for n in range(tries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=HDRS), timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception:
            if n == tries - 1:
                raise
            time.sleep(2 ** n)


def load_store():
    return json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else []


def save_store(rows):
    """id 오름차순 정렬 저장 — 빌더의 페이지 경계를 고정하기 위한 핵심."""
    rows.sort(key=lambda r: int(r["id"]))
    os.makedirs(DATA, exist_ok=True)
    json.dump(rows, open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def norm(r, seen_on):
    """위젯 API 응답 → 스토어 레코드.

    product_no 는 **리뷰 자신의 소속 상품**이다. 조회에 쓴 product_no 가 아니다.
    작성일은 본문에서 건질 수 있으면 그것을 쓰고, 못 건지면 수집일을 넣되
    date_estimated=True 로 표시한다. 빌더는 추정 날짜를 화면에 내보내지 않는다 —
    오래된 후기에 수집일을 붙이면 날짜를 조작한 것처럼 보이기 때문이다.
    """
    content = (r.get("content") or "").strip()
    prod = r.get("product") or {}
    m = EMBEDDED_DATE.search(content)
    return {"id": str(r.get("id")),
            "product_no": prod.get("product_no"),
            "product_name": prod.get("product_name") or "",
            "ratings": r.get("ratings"), "content": content,
            "option": r.get("product_option") or "",
            "date": m.group(1) if m else seen_on,
            "date_estimated": not m}


def _walk(product_no, pages, by_id, today, delay, early_stop, save_every=0):
    """공통 순회. 새로 담은 레코드 수를 돌려준다."""
    before, misses = len(by_id), 0
    for page in range(1, pages + 1):
        if early_stop and misses >= MISS_TOLERANCE:
            break
        try:
            rows = api(product_no=product_no, page=page, page_size=3)
        except Exception as e:
            print(f"    page {page} 포기: {e}", file=sys.stderr)
            break
        if not rows:
            break
        fresh = 0
        for r in rows:
            rid = str(r.get("id"))
            if rid in by_id:
                # 이미 아는 리뷰라도 상품 정보가 비어 있으면 채운다
                prod = r.get("product") or {}
                if not by_id[rid].get("product_no") and prod.get("product_no"):
                    by_id[rid]["product_no"] = prod["product_no"]
                    by_id[rid]["product_name"] = prod.get("product_name") or ""
            else:
                by_id[rid] = norm(r, today)
                fresh += 1
        misses = 0 if fresh else misses + 1
        if save_every and page % save_every == 0:
            save_store(list(by_id.values()))
            print(f"    page {page}/{pages} · 스토어 {len(by_id):,}건", flush=True)
        time.sleep(delay)
    return len(by_id) - before


def sync_api(delay=0.35):
    """전 상품을 훑어 신규만 담는다. 페이지 예산 안에서만 걷는다."""
    by_id = {r["id"]: r for r in load_store()}
    today, total_new = date.today().isoformat(), 0
    for p in products():
        n = _walk(p["product_no"], min(PAGE_CLAMP, MAX_PAGES_INCREMENTAL),
                  by_id, today, delay, early_stop=True)
        total_new += n
        print(f"  조회 {p['product_no']:>3} ({p['slug']}): 신규 {n}건")
    save_store(list(by_id.values()))
    return total_new, len(by_id)


def backfill_api(product_no, delay=0.5):
    """위젯 API 가 허용하는 전 구간(page 1~499)을 걷는다. 조기 종료하지 않으므로
    연결이 끊겨도 다시 돌리면 빠진 구간을 채운다."""
    by_id = {r["id"]: r for r in load_store()}
    n = _walk(product_no, PAGE_CLAMP, by_id, date.today().isoformat(),
              delay, early_stop=False, save_every=25)
    save_store(list(by_id.values()))
    return n, len(by_id)


# 상품명으로 특정할 수 없고 제품 리뷰도 아닌 것은 아예 받지 않는다.
CSV_EXCLUDE = ("BPC 시즌3 참가신청",)

CSV_COLS = {"id": ("리뷰번호", "리뷰ID", "리뷰no", "번호", "id"),
            "ratings": ("평점", "별점", "만족도", "rating"),
            "content": ("리뷰내용", "리뷰본문", "내용", "본문", "content"),
            "date": ("작성일", "등록일", "작성일시", "date"),
            "product_name": ("상품명", "상품", "product"),
            "option": ("옵션", "상품옵션", "option")}


def pick(row, names):
    for n in names:
        for k in row:
            if k and n in k.replace(" ", ""):
                return (row[k] or "").strip()
    return ""


def resolve_product(name, prods):
    """CSV 의 상품명 → product_no.

    알파리뷰 엑셀의 상품명은 사이트의 상품명과 표기가 다르다. 같은 상품인데
    `[설인아 PICK]` 같은 기획전 접두어가 붙고, `데이팩(6ea)` / `데이팩 (6ea)` 처럼
    공백이 다르다. 그래서 products.json 의 aliases 로 먼저 정확히 맞춰보고,
    안 되면 공백·대괄호를 지운 정규화 문자열로 포함 관계를 본다.
    """
    name = (name or "").strip()
    for p in prods:                                    # ① alias 완전 일치
        if name in (p.get("aliases") or []):
            return p["product_no"]
    def key(s):                                        # 모듈의 norm() 과 다른 것이다
        return re.sub(r"[\s\[\]()·+&]", "", s or "")
    n = key(name)
    for p in prods:                                    # ② 정규화 포함 관계
        for cand in [p["name"]] + (p.get("aliases") or []):
            c = key(cand)
            if c and (c in n or n in c):
                return p["product_no"]
    return None


def sync_csv(path):
    """엑셀 내보내기 CSV 병합. 상품명으로 product_no 를 되찾는다."""
    prods = products()
    by_id = {r["id"]: r for r in load_store()}
    new, updated, unmatched = 0, 0, set()
    skipped = 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rec = {k: pick(row, v) for k, v in CSV_COLS.items()}
            if not rec["content"]:
                continue
            if any(x in rec["product_name"] for x in CSV_EXCLUDE):
                skipped += 1
                continue
            pno = resolve_product(rec["product_name"], prods)
            if pno is None:
                unmatched.add(rec["product_name"])
            rid = rec["id"]
            if not rid:
                # 리뷰번호가 없으면 id 로 중복을 가릴 수 없다. 리뷰 절반이 정형문구라
                # 본문으로 중복을 판정하면 서로 다른 사람의 리뷰가 지워진다.
                raise SystemExit(
                    "리뷰번호(리뷰ID) 컬럼이 없다. 엑셀 내보내기에서 리뷰번호를 포함해 "
                    "재신청해야 한다 — 본문만으로는 중복을 가릴 수 없다.")
            fields = {"product_no": pno, "product_name": rec["product_name"],
                      "ratings": rec["ratings"] or None, "content": rec["content"],
                      "option": rec["option"], "date": rec["date"][:10],
                      "date_estimated": False}
            if rid in by_id:
                by_id[rid].update(fields); updated += 1       # 실제 작성일로 갱신
            else:
                by_id[rid] = {"id": rid, **fields}; new += 1
    save_store(list(by_id.values()))
    if skipped:
        print(f"  제외 {skipped}건 (제품 리뷰가 아닌 항목)")
    if unmatched:
        print(f"  ⚠ 상품 매칭 실패 {len(unmatched)}종 — products.json 의 aliases 에 추가:")
        for u in sorted(unmatched)[:12]:
            print(f"      {u}")
    return new, updated, len(by_id)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", action="store_true", help="전 상품 신규만 수집 (매일)")
    ap.add_argument("--deep", type=int, metavar="PRODUCT_NO",
                    help="해당 product_no 로 API 전 구간 백필. 재실행하면 이어진다")
    ap.add_argument("--csv", help="알파리뷰 엑셀 내보내기 CSV")
    a = ap.parse_args()
    if not (a.api or a.deep or a.csv):
        sys.exit("--api / --deep / --csv 중 하나 필요")

    if a.csv:
        print(f"CSV 백필: {a.csv}")
        new, upd, total = sync_csv(a.csv)
        print(f"→ 신규 {new:,}건 · 작성일 갱신 {upd:,}건 · 스토어 {total:,}건")

    if a.deep:
        print(f"전 구간 백필: product_no={a.deep}")
        n, total = backfill_api(a.deep)
        print(f"→ 신규 {n:,}건 · 스토어 {total:,}건")

    if a.api:
        new, total = sync_api()
        print(f"→ 신규 {new:,}건 · 스토어 {total:,}건")


if __name__ == "__main__":
    main()
