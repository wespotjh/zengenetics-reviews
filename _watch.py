#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카페24 상품 상세페이지 감시.

카페24가 상세설명에 넣은 <script type="application/ld+json"> 을 하룻밤 뒤에
제거한 일이 있었다(칼륨·마그네슘·비타민B). 이미지와 alt, style/result/filesize
같은 비표준 속성은 그대로였고 <script> 만 사라졌다. 저장 직후에는 남아 있었고
다음 날 없어졌으므로 주기적으로 도는 작업이다.

사람이 눈으로 볼 때까지 모르는 상황을 없애기 위해, 매일 10개 상품 페이지의
지표를 재서 지난번보다 줄어들면 실패로 끝낸다. 무엇이 몇에서 몇으로 줄었는지
로그에 남는다.

지표가 늘어나는 것(작업 반영)은 정상이므로 기준선을 갱신한다.
"""
import json, os, re, sys, time, html, urllib.request

BASE = "https://zengenetics.co.kr/product/detail.html?product_no="
STATE = "data/pagewatch.json"

# product_no → (이름, 기대 이미지 수, 기대 질문 수, 본문에 반드시 있어야 하는 문구).
#
# 기대값을 고정해 두는 이유: 지난 기준선과만 비교하면 한 번 망가진 값이 새 기준선이
# 되어 그 뒤로는 계속 "정상"이 된다. 실제로 마그네슘 본편(16)에 데이팩 파일이
# 붙여진 것을 감시가 한 번 잡은 뒤, 고장난 값이 기준선이 되어 다음 실행에서
# 통과시켜 버렸다.
#
# 마커는 그 상품에만 있는 문구다. 16과 61은 이미지가 둘 다 16개여서 개수로는
# 구분되지 않고, 파일을 서로 바꿔 붙이면 마커로만 잡힌다.
PRODUCTS = [
    (11, "칼륨 (20ea)",     14, 5, "왜 붓기 관리에 칼륨이 좋은가요?"),
    (16, "마그네슘 (20ea)",  16, 5, "운동하는 날만 먹어도 되나요?"),
    (13, "비타민B (20ea)",   15, 5, "언제 먹는게 가장 좋은가요?"),
    (63, "붓기부스터 SET",    25, 5, "칼륨이 2박스인 이유가 있나요?"),
    (64, "퍼포먼스 SET",     27, 5, "마그네슘과 비타민B를 왜 같이 먹나요?"),
    (98, "칼마비 SET",       15, 5, "세 가지를 같이 먹는 이유가 뭔가요?"),
    (60, "칼륨 데이팩",       14, 3, "칼륨은 1일 2회 1회 1포 섭취라 6포는 3일분입니다"),
    (61, "마그네슘 데이팩",    16, 3, "마그네슘은 1일 1회 1포 섭취라 6포는 6일분입니다"),
    (62, "비타민B 데이팩",    15, 3, "비타민B컴플렉스는 1일 1회 1포 섭취라 6포는 6일분입니다"),
    (71, "생애첫구매",        19, 5, "어떤 걸 고르면 되나요?"),
]

# 줄어들면 안 되는 지표. 늘어나는 건 작업이 반영된 것이므로 기준선을 올린다.
METRICS = ("images", "alt", "faq_jsonld", "faq_micro", "korean")


def fetch(no):
    url = f"{BASE}{no}&cb={int(time.time()*1000)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (zengenetics page watch)",
        "Cache-Control": "no-cache", "Pragma": "no-cache"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def detail_region(s):
    """상세설명 영역만 잘라낸다. 스킨 공통 영역의 숫자가 섞이면 지표가 흐려진다."""
    i = s.find("prdDetail")
    seg = s[i:i + 250000] if i >= 0 else s
    for mark in ('id="prdReview"', "상품 사용후기"):
        e = seg.find(mark)
        if e > 0:
            return seg[:e]
    return seg


def measure(s):
    seg = detail_region(s)
    imgs = re.findall(r"<img[^>]+NNEditor[^>]*>", seg)
    jsonld = 0
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(blk.strip())
        except ValueError:
            continue
        if d.get("@type") == "FAQPage":
            jsonld = len(d.get("mainEntity", []))
    txt = re.sub(r"<script.*?</script>", "", seg, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    alts = " ".join(html.unescape(a) for a in re.findall(r'alt="([^"]*)"', seg))
    return {
        "_text": txt + " " + alts,
        "images": len(imgs),
        "alt": sum(1 for t in imgs if "alt=" in t),
        "faq_jsonld": jsonld,
        "faq_micro": len(re.findall(r'itemtype="https://schema\.org/Question"', seg)),
        "korean": len(re.findall(r"[가-힣]", txt + " " + alts)),
        "review_link": int("review.zengenetics.co.kr" in seg),
    }


def main():
    prev = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    cur, problems = {}, []

    print(f"{'no':>3}  {'상품':<16} {'이미지':>9} {'alt':>7} {'JSON-LD':>9} "
          f"{'micro':>7} {'한글':>8}")
    print("-" * 68)
    for no, name, want_img, want_q, marker in PRODUCTS:
        key = str(no)
        try:
            m = measure(fetch(no))
        except Exception as e:                      # 네트워크 실패는 지표 하락이 아니다
            problems.append(f"{no} {name}: 조회 실패 — {e}")
            print(f"{no:>3}  {name:<16} 조회 실패")
            continue
        text = m.pop("_text")
        cur[key] = m
        old = prev.get(key, {})

        flags = []
        if m["images"] != want_img:
            flags.append(f"이미지 {m['images']}개 (기대 {want_img})")
        if m["alt"] != m["images"]:
            flags.append(f"alt {m['alt']}/{m['images']}")
        if not m["review_link"]:
            flags.append("리뷰 링크 없음")
        # 기대 질문 수 — 기준선과 무관하게 절대값으로 본다
        if m["faq_micro"] != want_q:
            flags.append(f"마이크로데이터 질문 {m['faq_micro']}개 (기대 {want_q})")
        # 마커 — 다른 상품의 파일이 붙여졌는지 잡는다
        if marker not in text:
            flags.append(f"이 상품 고유 문구 없음: {marker!r}")
        if "(주)위스팟바이오랩" not in text:
            flags.append("회사명 (주)위스팟바이오랩 표기 없음")
        if re.search(r"위스팟(?!바이오랩)", text):
            flags.append("구 회사명 표기 잔존")
        for k in METRICS:
            if k in old and m[k] < old[k]:
                flags.append(f"{k} {old[k]}→{m[k]} 감소")

        mark = "✅" if not flags else "❌"
        print(f"{no:>3}  {name:<16} {m['images']:>4}/{want_img:<4} {m['alt']:>7} "
              f"{m['faq_jsonld']:>9} {m['faq_micro']:>7} {m['korean']:>8,} {mark}")
        for f in flags:
            problems.append(f"{no} {name}: {f}")

    # 기준선 갱신. 조회 실패한 제품은 이전 값을 유지한다.
    merged = dict(prev)
    merged.update(cur)
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    print()
    if problems:
        print("문제 발견:")
        for p in problems:
            print("  -", p)
        return 1
    print("10개 상품 모두 정상 — 지표 하락 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
