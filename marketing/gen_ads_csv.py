# -*- coding: utf-8 -*-
"""구글 시트가 IMPORTDATA 로 당겨갈 일별 실적 CSV 를 만든다.

매일 09:30 Routine 이 Windsor 에서 조회한 값을 DAILY 에 추가하고 이 스크립트를 다시 실행,
data/ads_daily.csv 를 커밋·푸시하면 구글 시트가 자동으로 갱신된다.
"""
import csv, io, os

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ads_daily.csv")

# (날짜, 캠페인, 노출, 클릭, 비용, 전환, 전환값)  — Windsor google_ads 조회값
DAILY = [
 ("2026-09-22", "브랜드 방어",   2, 0,     0, 0, 0),
 ("2026-09-22", "붓기",        667, 9, 15785, 0, 0),
 ("2026-09-22", "칼륨",         10, 0,     0, 0, 0),
 ("2026-09-23", "브랜드 방어",   7, 1,   889, 0, 0),
 ("2026-09-23", "붓기",       1185,19, 28140, 0, 0),
 ("2026-09-23", "칼륨",         77, 1,  1379, 0, 0),
]

# (날짜, 세션, 거래수, 매출) — Windsor googleanalytics4 조회값
GA4 = [
 ("2026-09-22", 1117, 14, 1553220),
 ("2026-09-23",  988,  7,  690900),
]
BASE_TX, BASE_REV = 15.8, 1485612   # 광고 전 기준선 (GA4 09-09~09-20 평균)

def build():
    ga = {d: (s, t, v) for d, s, t, v in GA4}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["날짜","캠페인","노출","클릭","CTR","평균CPC","비용",
                "전환","전환값","CPA","ROAS","GA4 거래수","GA4 매출","기준선 대비"])
    seen = set()
    for d, camp, imp, clk, cost, conv, cval in DAILY:
        ctr  = f"{clk/imp*100:.2f}%" if imp else ""
        cpc  = round(cost/clk) if clk else ""
        cpa  = round(cost/conv) if conv else ""
        roas = f"{cval/cost:.2f}" if cost else ""
        # GA4 전체 매출은 날짜당 1회만 표기 (캠페인별로 쪼갤 수 없음)
        if d in ga and d not in seen:
            seen.add(d)
            s, t, v = ga[d]
            diff = f"{(v/BASE_REV-1)*100:+.1f}%"
            g_t, g_v = t, v
        else:
            g_t, g_v, diff = "", "", ""
        w.writerow([d, camp, imp, clk, ctr, cpc, cost, conv, cval, cpa, roas, g_t, g_v, diff])

    # 합계
    ti = sum(r[2] for r in DAILY); tc = sum(r[3] for r in DAILY)
    ts = sum(r[4] for r in DAILY); tv = sum(r[6] for r in DAILY)
    tn = sum(r[5] for r in DAILY)
    w.writerow([])
    w.writerow(["누적","", ti, tc,
                f"{tc/ti*100:.2f}%" if ti else "",
                round(ts/tc) if tc else "", ts, tn, tv,
                round(ts/tn) if tn else "",
                f"{tv/ts:.2f}" if ts else "", "", "", ""])
    w.writerow([])
    w.writerow(["광고 전 기준선", f"일 거래 {BASE_TX}건 / 일 매출 {BASE_REV:,}원 (GA4 09-09~09-20 평균)"])
    w.writerow(["갱신", "매일 09:30 KST 자동. 이 시트는 GitHub 의 CSV 를 IMPORTDATA 로 당겨옵니다."])
    return buf.getvalue()

if __name__ == "__main__":
    data = build()
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(data)
    print(data)
