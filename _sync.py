#!/usr/bin/env python3
"""
리뷰 스토어 증분 동기화.

두 가지 입력을 같은 스토어(data/<slug>.json)에 병합한다.

  1) 알파리뷰 위젯 API  — 신규 리뷰. 항상 1페이지에 들어오므로 아는 id 를
     만나면 멈춘다. 매일 돌려도 요청 몇 건이면 끝난다.
  2) 알파리뷰 엑셀 내보내기 CSV — 과거 이력 백필(1회). 위젯 API 는 page 500
     에서 클램프되어 상품당 약 1,497건만 꺼낼 수 있어 전량은 이 경로로만 온다.

스토어는 id 오름차순(과거→최신)으로 정렬해 저장한다. 빌더가 이 순서로 페이지를
끊기 때문에 기존 페이지 URL 과 내용이 흔들리지 않는다.

사용:
  python3 _sync.py --api potassium              신규만 (매일)
  python3 _sync.py --api all                    전 상품 신규
  python3 _sync.py --csv export.csv             백필 병합
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date

HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(HERE, "data")
BASE  = "https://review-widget.alphwidget.com/v2/api-widget"
MALL, SHOP, WIDGET = "wespotjo", "1", "7ee3b8bd"
HDRS = {"Referer": "https://zengenetics.co.kr/", "Origin": "https://zengenetics.co.kr",
        "Accept": "application/json", "User-Agent": "zengenetics-review-sync/1.0"}
PAGE_CLAMP = 499          # 500 이후는 같은 3건이 반복된다 (이진탐색 확인)

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

def store_path(slug): return os.path.join(DATA, f"{slug}.json")

def load_store(slug):
    p = store_path(slug)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []

def save_store(slug, rows):
    """id 오름차순으로 정렬 저장 — 페이지 경계를 고정하기 위한 핵심."""
    rows.sort(key=lambda r: int(r["id"]))
    json.dump(rows, open(store_path(slug), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

# 이관된 네이버페이 구매평은 본문 끝에 실제 작성일이 박혀 있다.
#   "잘받았습니다.좋아요.,(2025-09-19 17:40:31 에 등록된 네이버 페이 구매평)"
# 위젯 API 응답에는 작성일 필드가 없으므로 이게 유일한 실제 날짜 출처다 (약 13%).
EMBEDDED_DATE = re.compile(r"\((\d{4}-\d{2}-\d{2})[^)]*에 등록된[^)]*\)")

def norm(r, seen_on):
    """위젯 API 응답 → 스토어 레코드.

    API 에 작성일 필드가 없다. 본문에서 실제 작성일을 건질 수 있으면 그것을 쓰고,
    못 건지면 수집일을 넣되 date_estimated=True 로 표시한다. 빌더는 추정 날짜를
    **화면에 표시하지 않는다** — 오래된 후기에 수집일을 붙이면 날짜를 조작한 것처럼
    보이기 때문이다."""
    content = (r.get("content") or "").strip()
    m = EMBEDDED_DATE.search(content)
    return {"id": str(r.get("id")), "ratings": r.get("ratings"),
            "content": content, "option": r.get("product_option") or "",
            "date": m.group(1) if m else seen_on,
            "date_estimated": not m}

# 위젯의 기본 정렬은 순수 최신순이 아니다. 앞머리에 **고정 노출 리뷰 4건**이
# 붙고(page 1 전체 + page 2 첫 항목), 그 뒤부터 id 내림차순(최신순)이 시작된다.
#   page 1 → 78633090, 75141298, 74012666
#   page 2 → 68037045, 99940570, 99919641   ← 여기서 최신순이 시작
# 따라서 "아는 id 를 만나면 중단"은 틀렸다. 고정 리뷰만 있는 page 1 에서 멈춰
# 신규를 영구히 놓친다. 신규가 없는 페이지가 MISS_TOLERANCE 번 연속 나올 때만 멈춘다.
MISS_TOLERANCE = 3

def sync_api(slug, product_no, delay=0.35):
    cur = load_store(slug)
    have = {r["id"] for r in cur}
    today, added, misses, page = date.today().isoformat(), [], 0, 1
    while page <= PAGE_CLAMP and misses < MISS_TOLERANCE:
        try:
            rows = api(product_no=product_no, page=page, page_size=3)
        except Exception as e:
            print(f"  {slug} page {page} 실패: {e}", file=sys.stderr); break
        if not rows: break
        fresh = [r for r in rows if str(r.get("id")) not in have]
        if fresh:
            added += [norm(r, today) for r in fresh]
            have.update(str(r.get("id")) for r in fresh)
            misses = 0
        else:
            misses += 1                   # 고정 리뷰 구간을 지나가기 위한 유예
        page += 1
        time.sleep(delay)
    if added:
        save_store(slug, cur + added)
    return len(added), api("/meta", product_no=product_no, page=1,
                           page_size=3).get("total_count", 0)

def backfill_api(slug, product_no, delay=0.5, save_every=25):
    """위젯 API 가 허용하는 전 구간(page 1~499)을 걷는다. 조기 종료하지 않으므로
    연결이 끊겨도 다시 돌리면 빠진 구간을 채운다. 주기적으로 저장해 진행분을 잃지 않는다."""
    cur = load_store(slug)
    by_id = {r["id"]: r for r in cur}
    today, before = date.today().isoformat(), len(by_id)
    for page in range(1, PAGE_CLAMP + 1):
        try:
            rows = api(product_no=product_no, page=page, page_size=3)
        except Exception as e:
            print(f"  {slug} page {page} 포기: {e}", file=sys.stderr)
            break
        if not rows:
            break
        for r in rows:
            rid = str(r.get("id"))
            if rid not in by_id:
                by_id[rid] = norm(r, today)
        if page % save_every == 0:
            save_store(slug, list(by_id.values()))
            print(f"    page {page}/{PAGE_CLAMP} · 누적 {len(by_id):,}건", flush=True)
        time.sleep(delay)
    save_store(slug, list(by_id.values()))
    return len(by_id) - before


CSV_COLS = {"id": ("리뷰번호", "리뷰ID", "번호", "id"),
            "ratings": ("평점", "별점", "만족도", "rating"),
            "content": ("리뷰내용", "리뷰본문", "내용", "본문", "content"),
            "date": ("작성일", "등록일", "작성일시", "date"),
            "product": ("상품명", "상품", "product"),
            "option": ("옵션", "상품옵션", "option")}

def pick(row, names):
    for n in names:
        for k in row:
            if k and n in k.replace(" ", ""):
                return (row[k] or "").strip()
    return ""

def sync_csv(path):
    """엑셀 내보내기 CSV 를 상품명으로 갈라 각 스토어에 병합."""
    by_name = {p["name"]: p for p in products()}
    buckets, unmatched = {}, set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rec = {k: pick(row, v) for k, v in CSV_COLS.items()}
            if not rec["content"]:
                continue
            prod = next((p for n, p in by_name.items() if n and n in rec["product"]), None)
            if not prod:
                unmatched.add(rec["product"]); continue
            buckets.setdefault(prod["slug"], []).append(
                {"id": rec["id"], "ratings": rec["ratings"] or None,
                 "content": rec["content"], "option": rec["option"],
                 "date": rec["date"][:10], "date_estimated": False})
    total = 0
    for slug, rows in buckets.items():
        cur = load_store(slug)
        have = {r["id"] for r in cur}
        # 내보내기 레코드가 우선 — 실제 작성일을 갖고 있다
        by_id = {r["id"]: r for r in cur}
        new = 0
        for r in rows:
            if r["id"] in have:
                by_id[r["id"]].update({"date": r["date"], "date_estimated": False,
                                       "content": r["content"]})
            else:
                by_id[r["id"]] = r; new += 1
        save_store(slug, list(by_id.values()))
        print(f"  {slug}: 신규 {new}건 / 스토어 {len(by_id)}건")
        total += new
    if unmatched:
        print(f"  ⚠ 상품 매칭 실패 {len(unmatched)}종 — products.json 에 추가 필요:")
        for u in sorted(unmatched)[:10]:
            print(f"      {u}")
    return total

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", help="신규만 수집할 상품 slug 또는 all (매일)")
    ap.add_argument("--deep", help="API 허용 전 구간 백필. 중단되면 다시 돌리면 이어진다")
    ap.add_argument("--csv", help="알파리뷰 엑셀 내보내기 CSV")
    a = ap.parse_args()
    if not (a.api or a.csv or a.deep): sys.exit("--api / --deep / --csv 중 하나 필요")

    if a.deep:
        targets = products() if a.deep == "all" else [p for p in products() if p["slug"] == a.deep]
        if not targets: sys.exit(f"알 수 없는 slug: {a.deep}")
        for p in targets:
            n = backfill_api(p["slug"], p["product_no"])
            print(f"  {p['slug']}: 백필 신규 {n:,}건 · 스토어 {len(load_store(p['slug'])):,}건")

    if a.csv:
        print(f"CSV 백필: {a.csv}")
        print(f"→ 신규 {sync_csv(a.csv):,}건 병합")

    if a.api:
        targets = products() if a.api == "all" else [p for p in products() if p["slug"] == a.api]
        if not targets: sys.exit(f"알 수 없는 slug: {a.api}")
        for p in targets:
            n, total = sync_api(p["slug"], p["product_no"])
            have = len(load_store(p["slug"]))
            print(f"  {p['slug']}: 신규 {n}건 · 스토어 {have:,}건 / 알파리뷰 보유 {total:,}건")

if __name__ == "__main__":
    main()
