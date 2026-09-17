#!/usr/bin/env python3
"""
리뷰 스토어 → 정적 사이트 (review.zengenetics.co.kr)

**리뷰 자신의 product_no 로 페이지를 나눈다.** 조회에 쓴 product_no 가 아니다 —
알파리뷰는 성분이 같은 상품군에 같은 리뷰 풀을 돌려주기 때문에, 조회 기준으로 나누면
같은 리뷰가 여러 페이지에 중복 게재된다(자세한 근거는 `_sync.py` 상단 주석).

**페이지 경계 고정.** 스토어를 id 오름차순(과거→최신)으로 놓고 PER_PAGE 씩 끊으면
신규 리뷰는 마지막 페이지에만 쌓인다. 기존 페이지의 URL 과 내용이 유지되므로
  - 매일 재배포되는 파일이 1~2개뿐이고
  - 이미 색인된 페이지 내용이 매일 뒤바뀌지 않는다 (색인 감점 회피)
대신 1페이지가 과거 리뷰가 되므로 허브는 최신 페이지를 앞에 놓는다.

**심의 설계 (건강기능식품 표시·광고)**
  1. 전량 게재, 작성 순서대로 — 골라 싣으면 이용후기가 아니라 광고가 된다
  2. 브랜드가 쓴 효능 문장 0줄 — 고객 원문과 중립 라벨(평점·날짜)만
  3. 화면에 보이는 리뷰만 Review 마크업 — 안 보이는 것을 넣으면 정책 위반

사용: python3 _build.py [--domain review.zengenetics.co.kr] [--out dist]
"""
import argparse, csv, html, json, os, re, shutil
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PER_PAGE = 50
LINK_PREFIX = "/"

# 칼륨의 인정 기능성은 나트륨 배출이다. 그 밖의 표현은 삭제하지 않고 분리해 검수에 넘긴다.
RISK = {"체중·다이어트": r"체중|몸무게|다이어트|감량|\d+\s*(kg|키로|킬로)|살\s*빠",
        "질병·치료":     r"치료|완치|질병|병원|약\s*대신|처방",
        "의학적 단정":   r"효과\s*보장|100%|무조건|반드시\s*낫"}

# 모든 상품에 항상 참인 문장만 둔다. 식품유형은 상품마다 다르므로 단정하지 않는다.
# 칼륨은 실측 결과 **당류가공품(일반식품)** 이다 — 건강기능식품이 아니다. 그런데도
# "건강기능식품은 …" 이라고 써 두면 제품 분류를 잘못 알리는 표시가 된다.
# products.json 의 food_type 이 있는 상품만 그 유형을 덧붙인다.
NOTE_BASE = ("본 페이지는 구매 고객이 작성한 이용후기를 작성 순서대로 그대로 게시한 "
             "것이며, 판매자가 선별하거나 편집하지 않았습니다. 개인의 후기이며 제품의 "
             "효과를 보증하지 않습니다. 본 제품은 의약품이 아니며 질병의 예방·치료를 "
             "목적으로 하지 않습니다.")


def claim_for(p=None):
    """기능성 문구 슬롯.

    products.json 의 functional_claim 에 값이 있으면 리뷰 페이지 상단에 렌더한다.
    비어 있으면 아무것도 나가지 않는다.

    **이 값은 식약처 인정(개별인정형) 또는 기능성 표시 식품 요건을 충족한 뒤에만 채운다.**
    칼륨 제품의 현재 식품유형은 당류가공품(일반식품)이고, 일반식품에 기능성·효능을
    표시하면 식품표시광고법 위반이다. 임상 결과만으로는 표시 권한이 생기지 않는다.
    인정 문구를 받으면 이 필드에 한 줄 넣으면 전 페이지에 반영된다 — 재작업 없다.
    """
    c = (p or {}).get("functional_claim")
    return f'<p class="claim">{esc(c)}</p>' if c else ""


def awards_for(p=None):
    """수상·랭킹 슬롯.

    products.json 의 awards 에 {"text": ..., "basis": ...} 목록이 있으면 렌더한다.
    측정 기준(매체·카테고리·기간)을 basis 로 반드시 함께 내보낸다. 기준 없는 1위
    표시는 객관적 근거 없는 최상급 표현이 된다.
    """
    aw = (p or {}).get("awards") or []
    if not aw:
        return ""
    li = "".join(f"<li>{esc(a['text'])}</li>" for a in aw)
    basis = " · ".join(a["basis"] for a in aw if a.get("basis"))
    out = f'<ul class="awards">{li}</ul>'
    if basis:
        out += f'<p class="basis">{esc(basis)}</p>'
    return out


def note_for(p=None):
    ft = (p or {}).get("food_type")
    if ft == "건강기능식품":
        # 건강기능식품에 "건강기능식품이 아닙니다" 를 붙이면 사실과 반대가 된다.
        return NOTE_BASE + " 본 제품의 식품유형은 건강기능식품입니다."
    if ft:
        return NOTE_BASE + f" 본 제품의 식품유형은 {ft}이며, 건강기능식품이 아닙니다."
    return NOTE_BASE

CSS = """*{box-sizing:border-box}
body{font:16px/1.7 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Segoe UI",sans-serif;
margin:0;color:#15161A;background:#fff}
.w{max-width:760px;margin:0 auto;padding:24px 20px 64px}
.awards{margin:10px 0 4px;padding-left:20px;font-weight:600}
.basis{margin:0 0 14px;font-size:12.5px;color:#93959D}
.agg{margin:6px 0 2px;font-size:15px;color:#15161A}
a{color:#1A2B6B}
h1{font-size:20px;margin:0 0 4px;line-height:1.35}
.sub{color:#5F626C;font-size:14px;margin:0 0 24px}
ul.rvs{list-style:none;padding:0;margin:0}
.rv{border-top:1px solid #E9E8E4;padding:18px 0}
.rv-h{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:#5F626C;margin-bottom:6px}
.rv-b{white-space:pre-wrap;word-break:break-word}
.rv-o{margin-top:8px;font-size:12.5px;color:#93959D}
.nav{margin-top:32px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.nav a{padding:8px 14px;border:1px solid #D8D6D0;border-radius:6px;text-decoration:none}
.hub{list-style:none;padding:0;margin:0}
.hub li{border-top:1px solid #E9E8E4;padding:14px 0}
.hub .n{color:#93959D;font-size:13px}
.hub .pages{margin-top:6px;display:flex;flex-wrap:wrap;gap:8px}
.hub .pages a{font-size:13px}
.claim{margin:0 0 14px;padding:10px 14px;border-left:3px solid #1A2B6B;background:#F4F6FC;font-size:14.5px}
.note{margin-top:40px;padding-top:16px;border-top:1px solid #E9E8E4;font-size:12.5px;color:#93959D}
@media (prefers-color-scheme:dark){
:root:not([data-theme="light"]) body{background:#141413;color:#EDEDEB}
:root:not([data-theme="light"]) a{color:#9DB2FF}
:root:not([data-theme="light"]) .rv,:root:not([data-theme="light"]) .hub li,
:root:not([data-theme="light"]) .note{border-color:#2E2E2B}
:root:not([data-theme="light"]) .nav a{border-color:#3A3A36}}"""


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


# 검색엔진 소유 확인용 meta 태그. data/verification/meta.txt 에 태그 원문을 한 줄씩
# 넣으면 전 페이지 <head> 에 그대로 들어간다 (Search Console 의 "HTML 태그" 방식).
VERIFY_META = ""


def load_verification():
    """data/verification/ 의 파일을 dist 루트로 그대로 복사하고, meta.txt 는 태그로 쓴다.

    Search Console 은 소유 확인에 ① HTML 파일 업로드(googleXXXX.html) ② HTML 태그
    두 방식을 쓴다. 둘 다 사이트에 뭔가를 올려야 하는데, 이 사이트는 우리가 빌드하므로
    여기에 넣어두면 배포가 알아서 처리한다. DNS 를 또 건드릴 필요가 없다.
    """
    global VERIFY_META
    src = os.path.join(DATA, "verification")
    files = []
    if not os.path.isdir(src):
        return files
    for fn in sorted(os.listdir(src)):
        path = os.path.join(src, fn)
        if not os.path.isfile(path):
            continue
        if fn.lower().endswith(".md"):
            continue                      # 이 폴더의 설명 문서는 배포 대상이 아니다
        if fn == "meta.txt":
            VERIFY_META = "\n".join(
                l.strip() for l in open(path, encoding="utf-8") if l.strip())
        else:
            files.append((fn, path))
    return files


def shell(title, desc, canon, body):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canon)}">
{VERIFY_META}
<style>{CSS}</style>
</head><body><div class="w">{body}</div></body></html>"""


def review_li(r):
    rating = r.get("ratings")
    # 추정 날짜(수집일)는 표시하지 않는다 — 실제 작성일이 확인된 것만 보여준다
    dt = "" if r.get("date_estimated") else (r.get("date") or "")
    body = esc(r["content"]).replace("\n", "<br>")
    rate = (f'<span itemprop="reviewRating" itemscope '
            f'itemtype="https://schema.org/Rating">평점 '
            f'<span itemprop="ratingValue">{esc(rating)}</span></span>') if rating else ""
    opt = f'<div class="rv-o">{esc(r["option"])}</div>' if r.get("option") else ""
    day = f'<span itemprop="datePublished" content="{esc(dt)}">{esc(dt)}</span>' if dt else ""
    return (f'<li class="rv" itemscope itemtype="https://schema.org/Review">'
            f'<div class="rv-h"><span>{rate}</span><span>{day}</span></div>'
            f'<div class="rv-b" itemprop="reviewBody">{body}</div>{opt}</li>')


def dedupe(rows):
    """같은 본문은 한 번만 게시한다.

    스토어에는 원본을 전부 남기지만, 사이트에는 같은 문장을 반복해 올리지 않는다.
    이유 두 가지:
      1) 간편리뷰 프리셋 때문에 서로 다른 고객이 같은 문장을 고르는 일이 많다.
         같은 문장을 100번 올려도 크롤러에게는 새 정보가 0이고, 중복 콘텐츠가 된다.
      2) 엑셀 내보내기와 위젯 API 의 리뷰 식별자 체계가 다르다(엑셀 `1008nJZbHNq`,
         API `78633090`). id 로는 같은 리뷰를 걸러낼 수 없어 본문으로 겹침을 막는다.

    남기는 것은 그 본문의 **가장 이른 작성일** 레코드다. 평점이 있는 쪽을 우선한다.
    """
    best = {}
    for r in rows:
        k = (r.get("content") or "").strip()
        cur = best.get(k)
        if cur is None:
            best[k] = r
            continue
        # 평점 보유 > 이른 작성일 > 낮은 seq
        def rank(x):
            return (0 if x.get("ratings") else 1,
                    x.get("date") or "9999-99-99",
                    x.get("seq") or 0)
        if rank(r) < rank(cur):
            best[k] = r
    out = list(best.values())
    out.sort(key=lambda r: r.get("seq") or 0)
    return out


def aggregate_ld(name, rows):
    """제품 단위 AggregateRating.

    카페24가 상품 페이지에 내보내는 reviewCount 는 419 로 고정되어 실제와 다르다.
    그 JSON-LD 는 우리가 고칠 수 없으므로, 리뷰 사이트에서 실제 집계를 따로 낸다.
    평점이 있는 레코드만 센다 — 없는 것을 세면 평균이 왜곡된다.
    """
    vals = [int(r["ratings"]) for r in rows
            if str(r.get("ratings") or "").strip().isdigit()]
    if len(vals) < 1:
        return None
    return {"@type": "AggregateRating",
            "ratingValue": round(sum(vals) / len(vals), 2),
            "reviewCount": len(vals),
            "bestRating": 5, "worstRating": 1}


def agg_html(agg):
    """평균 평점을 화면에도 낸다. 마이크로데이터는 화면에 보이는 값에만 붙인다."""
    if not agg:
        return ""
    return (f'<p class="agg" itemprop="aggregateRating" itemscope '
            f'itemtype="https://schema.org/AggregateRating">'
            f'평균 <strong itemprop="ratingValue">{agg["ratingValue"]}</strong> / 5 · '
            f'<span itemprop="reviewCount">{agg["reviewCount"]:,}</span>건'
            f'<meta itemprop="bestRating" content="5">'
            f'<meta itemprop="worstRating" content="1"></p>')


def build_group(slug, name, rows, domain, out, prod=None):
    rows = dedupe(rows)
    agg = aggregate_ld(name, rows)
    pages = [rows[i:i + PER_PAGE] for i in range(0, len(rows), PER_PAGE)] or [[]]
    urls = []
    for i, chunk in enumerate(pages, 1):
        fn = f"{slug}-{i}.html"
        canon = f"https://{domain}/{fn}"
        nav = []
        if i > 1:
            nav.append(f'<a href="{LINK_PREFIX}{slug}-{i - 1}.html" rel="prev">이전</a>')
        if i < len(pages):
            nav.append(f'<a href="{LINK_PREFIX}{slug}-{i + 1}.html" rel="next">다음</a>')
        nav.append(f'<a href="{LINK_PREFIX or "./"}">전체 목록</a>')
        ld = [{"@type": "Review",
               "reviewRating": {"@type": "Rating", "ratingValue": r["ratings"]},
               "reviewBody": r["content"][:1500]} for r in chunk if r.get("ratings")]
        # 평점이 있는 리뷰가 없으면 JSON-LD 를 아예 내보내지 않는다. 빈 ItemList 는
        # 아무 정보도 주지 않는다. 이번 내보내기에 평점 컬럼이 빠져 대부분이 여기 해당한다.
        doc = {"@context": "https://schema.org", "@type": "ItemList",
               "name": f"{name} 구매 후기", "numberOfItems": len(ld),
               "itemListElement": ld} if ld else None
        # 1페이지에만 제품 단위 집계를 얹는다. 모든 페이지에 넣으면 같은 집계가
        # 수십 번 중복 선언되어 구글이 어느 것을 믿을지 모호해진다.
        if agg and i == 1:
            doc = {"@context": "https://schema.org", "@type": "Product",
                   "name": name, "aggregateRating": {k: v for k, v in agg.items()},
                   "review": ld[:20]}
        jsonld = json.dumps(doc, ensure_ascii=False) if doc else ""
        body = (
            f'<h1>{esc(name)} 구매 후기</h1>'
            + awards_for(prod)
            + claim_for(prod)
            + agg_html(agg)
            + f'<p class="sub">총 {len(rows):,}건 · {i}/{len(pages)}페이지 · '
              f'구매 고객이 직접 작성한 이용후기입니다.</p>'
            + f'<ul class="rvs">{"".join(review_li(r) for r in chunk)}</ul>'
            + f'<div class="nav">{"".join(nav)}</div>'
            + f'<p class="note">{note_for(prod)}</p>'
            + (f'<script type="application/ld+json">{jsonld}</script>' if jsonld else "")
        )
        open(os.path.join(out, fn), "w", encoding="utf-8").write(shell(
            f"{name} 구매 후기 {i}/{len(pages)}페이지",
            f"{name} 구매 고객이 직접 작성한 이용후기 {len(rows):,}건 중 {i}페이지.",
            canon, body))
        urls.append(canon)
    return urls, len(pages), len(rows)


def build(domain, out):
    # 기본 Pages 주소(wespotjh.github.io/zengenetics-reviews/)는 하위 경로를 갖는다.
    # 링크를 "/xxx.html" 로 쓰면 루트로 가서 깨지므로 상대경로로 낸다.
    global LINK_PREFIX
    LINK_PREFIX = "" if "/" in domain else "/"
    # canonical/sitemap 은 아래 f-string 들이 https://{domain}/ 로 조립한다
    verify_files = load_verification()
    store = json.load(open(os.path.join(DATA, "reviews.json"), encoding="utf-8"))
    prods = {p["product_no"]: p for p in
             json.load(open(os.path.join(DATA, "products.json"), encoding="utf-8"))}
    # 매번 비우고 짓는다. 남겨두면 이전 빌드의 페이지가 그대로 배포되어,
    # 스토어에서 빠진 리뷰가 계속 게시된다(자체작업분 정리 때 실제로 겪었다).
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)

    # 리뷰 자신의 product_no 로 묶는다. 어떤 리뷰도 두 번 게재되지 않는다.
    groups, orphans = defaultdict(list), []
    for r in store:
        if not r.get("content"):
            continue
        p = prods.get(r.get("product_no"))
        (groups[p["slug"]] if p else orphans).append(r)

    all_urls, hub, flagged = [f"https://{domain}/"], [], []
    # product_no 오름차순. 단 기획전 그룹(음수 product_no)은 맨 뒤로 보낸다.
    for pno, p in sorted(prods.items(), key=lambda kv: (kv[0] < 0, kv[0])):
        rows = groups.get(p["slug"])
        if not rows:
            continue
        rows.sort(key=lambda r: r.get("seq") or 0)   # 스토어 진입 순서 = 페이지 경계 고정
        urls, npages, shown = build_group(p["slug"], p["name"], rows, domain, out, p)
        all_urls += urls
        hub.append((p, shown, npages))
        for r in rows:
            hits = [lab for lab, pat in RISK.items() if re.search(pat, r["content"])]
            if hits:
                flagged.append({"slug": p["slug"], "id": r["id"],
                                "ratings": r.get("ratings"), "date": r.get("date"),
                                "사유": " / ".join(hits), "content": r["content"]})

    total = sum(c for _, c, _ in hub)
    items = "".join(
        f'<li><a href="{LINK_PREFIX}{p["slug"]}-{n}.html">{esc(p["name"])}</a>'
        f'<div class="n">{cnt:,}건 · {n}페이지</div>'
        f'<div class="pages">'
        + " ".join(f'<a href="{LINK_PREFIX}{p["slug"]}-{i}.html">{i}</a>' for i in range(n, 0, -1))
        + '</div></li>' for p, cnt, n in hub)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(shell(
        "젠제네틱스 구매 후기",
        f"젠제네틱스 제품 구매 고객이 직접 작성한 이용후기 {total:,}건.",
        f"https://{domain}/",
        f'<h1>젠제네틱스 구매 후기</h1>'
        f'<p class="sub">총 {total:,}건 · 구매 고객이 직접 작성한 이용후기입니다. '
        f'각 줄의 첫 번호가 최신 페이지입니다.</p>'
        f'<ul class="hub">{items}</ul><p class="note">{NOTE_BASE}</p>'))

    open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in all_urls) + "</urlset>\n")
    open(os.path.join(out, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: https://{domain}/sitemap.xml\n")
    # CNAME 은 커스텀 도메인일 때만 쓴다. github.io 기본 주소로 배포할 때 이 파일이
    # 있으면 Pages 가 아직 붙지 않은 도메인으로 강제 전환하려 해서 사이트가 안 뜬다.
    cname = os.path.join(out, "CNAME")
    if domain.endswith(".github.io") or "/" in domain:
        if os.path.exists(cname):
            os.remove(cname)
    else:
        open(cname, "w", encoding="utf-8").write(domain + "\n")

    for fn, path in verify_files:
        shutil.copyfile(path, os.path.join(out, fn))

    if flagged:
        with open(os.path.join(out, "심의검토_대상.csv"), "w",
                  encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["slug", "id", "ratings", "date",
                                              "사유", "content"])
            w.writeheader(); w.writerows(flagged)

    chars = sum(len(r["content"]) for rows in groups.values() for r in rows)
    print(f"상품 {len(hub)}종 · 리뷰 {total:,}건 · 페이지 {len(all_urls) - 1}장 → {out}/")
    for p, cnt, n in hub:
        print(f"    {p['slug']:<20} {cnt:>6,}건 · {n:>3}페이지")
    if orphans:
        names = sorted({r.get("product_name") or "(상품명 없음)" for r in orphans})
        print(f"  ⚠ products.json 에 없는 상품의 리뷰 {len(orphans):,}건은 제외됐다:")
        for nm in names[:8]:
            print(f"      {nm}")
    print(f"크롤러가 읽을 본문 {chars:,}자 (카페24 상세페이지는 130자)")
    if verify_files or VERIFY_META:
        bits = [fn for fn, _ in verify_files] + (["meta 태그"] if VERIFY_META else [])
        print(f"소유 확인: {', '.join(bits)}")
    print(f"심의 검토 대상 {len(flagged)}건" + (" → 심의검토_대상.csv" if flagged else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="review.zengenetics.co.kr")
    ap.add_argument("--out", default=os.path.join(HERE, "dist"))
    a = ap.parse_args()
    build(a.domain, a.out)
