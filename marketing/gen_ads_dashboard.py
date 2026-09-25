# -*- coding: utf-8 -*-
"""젠제네틱스 검색광고 콘솔 (Artifact용 단일 HTML 생성).

일별 실적이 생기면 DAILY 에 넣고 다시 실행한다.
"""
import unicodedata as ud, datetime, html, io

ACCOUNT, START = "798-667-9268", "2026-09-22"
GEN = "2026-09-25"

CAMPAIGNS = [
    ("브랜드 방어", "젠제네틱스_브랜드방어_검색", "24281447473", 10000, 1500, 17,
     "이미 우리를 아는 사람이 이름으로 검색할 때. CPC가 가장 싸고 전환이 가장 확실합니다."),
    ("붓기",       "젠제네틱스_붓기_검색",       "24270384426", 20000, 2500, 14,
     "붓기 해결책을 찾는 신규 수요. 예산을 가장 많이 배분했습니다."),
    ("칼륨",       "젠제네틱스_칼륨_검색",       "24275789225", 10000, 2000, 11,
     "성분을 알고 찾는 수요. 구매 의도가 또렷합니다."),
]
TOTAL_BUDGET = sum(c[3] for c in CAMPAIGNS)

KW = {
 "브랜드 방어": [("젠제네틱스","완전"),("젠제네틱스","구문"),("젠제네틱스 칼륨","구문"),
  ("젠제네틱스 붓기","구문"),("젠제네틱스 후기","구문"),("젠제네틱스 공식몰","구문"),
  ("젠제네틱스 마그네슘","구문"),("젠제네틱스 비타민B","구문"),("젠제네틱스 붓기파우더","구문"),
  ("zengenetics","완전"),("zengenetics","구문"),("zen genetics","구문"),("zengenetic","구문"),
  ("zengenetics korea","구문"),("zengenetics official","구문"),
  ("위스팟바이오랩","구문"),("wespot biolab","구문")],
 "붓기": [("붓기 영양제","구문"),("붓기 제거","구문"),("붓기 빼는 법","구문"),("붓기파우더","구문"),
  ("붓기 보조제","구문"),("얼굴 붓기","구문"),("다리 붓기","구문"),("종아리 붓기","구문"),
  ("아침 붓기","구문"),("붓기 차","구문"),("부종 영양제","구문"),("수분 배출","구문"),
  ("붓기 영양제","확장"),("붓기 칼륨","확장")],
 "칼륨": [("칼륨 영양제","구문"),("칼륨 보충제","구문"),("포타슘 영양제","구문"),("구연산 칼륨","구문"),
  ("칼륨 파우더","구문"),("칼륨 스틱","구문"),("potassium 영양제","구문"),("칼륨 효능","구문"),
  ("칼륨 부족","구문"),("전해질 영양제","구문"),("칼륨 영양제","확장")],
}
NEG_GROUPS = [
 ("의약품·의료", ["의약품","이뇨제","다이어트약","병원","처방","약국"], True),
 ("무료·체험",   ["무료","공짜"], False),
 ("부정 이슈",   ["부작용","후유증","소송","리콜"], False),
 ("기존 고객 CS",["환불","해지"], False),
 ("구직",        ["알바","채용","구인","연봉"], False),
 ("투자",        ["주가","상장"], False),
 ("B2B",         ["도매","총판","대리점","제조사","OEM","ODM"], False),
 ("직접 만들기", ["레시피","만들기","DIY"], False),
 ("무관",        ["토렌트","중고"], False),
 ("부상·질환 (9/24 추가)", ["무릎","인대","멍","다래끼","잇몸","갑상선",
                            "하지정맥류","림프","염증","거상","윤곽","복숭아뼈"], False),
 ("다른 해결책 (9/24 추가)", ["찜질","캔디","연고","한약","다이소","기구",
                              "요가","홈트","반신욕","편의점","대처법"], False),
 ("타사 제품 (9/24 추가)", ["파인셔스","파인 셔스","알파플러스","알파 플러스",
                            "디스웰러","모미차","보람차","아이돌차"], False),
 ("검색 파트너 누수 (9/25 추가, 두 캠페인)",
  ["식품","건강식품","건강기능식품","건강보조식품","기능성식품","영양제 사이트",
   "헬스케어몰","아이허브","아로나민","칼슘","면역력","갱년기","청소년",
   "저탄고지","변비","원픽","쇼핑몰","선물","blackmore"], True),
 ("정보성 (9/23 추가)", ["마사지","스트레칭","운동","혈자리","지압","주파수","자세",
                          "약초","민간요법","템","치료","원인","이유","증상","음식","음료","주스",
                          "호박","약","모기","강아지","크레아틴","폼롤러","양말","라면","혀",
                          "성형","수술","쌍수","쌍꺼풀","필러","사랑니","골절","치질","절개",
                          "임산부","산후","출산","디시","더쿠"], True),
]
HL = {
"브랜드 방어": ["젠제네틱스 공식몰","젠제네틱스 붓기파우더","붓기파우더 공식 판매처","젠제네틱스 칼륨 525mg",
 "올리브영 건강식품 1위","쿠팡 붓기 검색 1위","재구매율 92%",
 "설인아 PICK 젠제네틱스","물없이 3초 분말스틱","독일 구연산 칼륨 원료","공식몰 최저가 구매",
 "젠제네틱스 Zengenetics 공식몰","무료배송 당일출고","생애 첫 구매 특가"],
"붓기": ["붓기파우더 젠제네틱스","붓기 영양제 칼륨","아침 얼굴 저녁 종아리","짠 음식 즐기는 분께",
 "칼륨 525mg 1일 2포","물없이 먹는 분말스틱","쿠팡 붓기 검색 1위","올리브영 건강식품 1위",
 "후기 333건 4.77점","독일 구연산 칼륨","칼륨 단일 설계","하루 2포 간편 루틴",
 "공식몰에서 구매","첫 구매 특가 확인","무료배송"],
"칼륨": ["칼륨 영양제 525mg","구연산 칼륨 1포 262mg","칼륨 1일기준치 15%","독일 Jungbunzlauer",
 "칼륨 단일 원료 설계","분말스틱 물없이 섭취","젠제네틱스 포타슘","칼륨 보충 하루 2포",
 "후기 333건 평점 4.77","올리브영 건강식품 1위","쿠팡 붓기 검색 1위","EP USP FCC 기준 충족",
 "공식몰 구매하기","무료배송 당일출고","첫 구매 특가"]}
DS = {
"브랜드 방어": ["[올리브영] 건강식품 실시간 랭킹 1위 기록. 무료배송·당일출고.",
 "웰니스 ALL DAY 루틴",
 "K-이너뷰티(14개국 수출) 미네랄 밸런스."],
"붓기": ["칼륨 525mg 하루 2포. 물 없이 먹는 분말스틱으로 간편하게 챙기세요.",
 "쿠팡 붓기 검색 1위·올리브영 건강식품 1위. 후기 333건 4.77점.",
 "독일 Jungbunzlauer 구연산 칼륨 단일 설계. 1포당 칼륨 262.5mg.",
 "생애 첫 구매 특가 진행 중. 데이팩 6포로 가볍게 시작해보세요."],
"칼륨": ["1포당 구연산 칼륨 262.5mg, 2포 525mg으로 1일 기준치의 15%입니다.",
 "독일 Jungbunzlauer 원료. EP·USP·FCC·EU 231/2012 기준 충족.",
 "정제가 아닌 분말스틱. 물 없이 뜯어서 바로 섭취할 수 있습니다.",
 "구매 후기 333건 평균 4.77점. 공식몰에서 첫 구매 특가 확인하세요."]}
EXT = [("사이트링크", "붓기 칼륨 · 구매 후기 · 첫 구매 특가 · 붓기 부스터 세트", "캠페인별 4개 (칼륨은 마그네슘)"),
       ("콜아웃", "무료배송 · 당일출고 · 올리브영 건강식품 1위 · 쿠팡 붓기 검색 1위", "캠페인별 4개"),
       ("구조화된 스니펫", "칼륨 / 마그네슘 / 비타민B컴플렉스 / 데이팩 / 세트", "유형 Types"),
       ("전화번호", "070-8872-1337", "국가 KR")]

GA4 = [("2026-09-09",1007,19,774700),("2026-09-10",1313,13,585300),("2026-09-11",1178,12,505340),
 ("2026-09-12",1597,24,2094824),("2026-09-13",932,15,1202910),("2026-09-14",934,11,1282462),
 ("2026-09-15",1304,25,2984991),("2026-09-16",1193,14,1738612),("2026-09-17",1246,11,1278524),
 ("2026-09-18",1094,11,973840),("2026-09-19",964,16,2342940),("2026-09-20",1251,19,2062900),
 ("2026-09-21",753,5,182560),("2026-09-22",1117,14,1553220),
 ("2026-09-23",1012,8,825800),("2026-09-24",1084,13,1007342),
 ("2026-09-25",336,0,0)]
BASE_N = 12
DAILY = [   # (날짜, 캠페인, 노출, 클릭, 비용, 전환, 전환값)
 ("2026-09-22", "붓기",       667, 9, 15785, 0, 0),
 ("2026-09-22", "칼륨",        10, 0,     0, 0, 0),
 ("2026-09-22", "브랜드 방어",   2, 0,     0, 0, 0),
 ("2026-09-23", "붓기",      1185,19, 28140, 0, 0),
 ("2026-09-23", "칼륨",        77, 1,  1379, 0, 0),
 ("2026-09-23", "브랜드 방어",   7, 1,   889, 0, 0),
 ("2026-09-24", "붓기",       913,17, 22180, 1, 38400),
 ("2026-09-24", "칼륨",       230,57, 16720, 0, 0),
 ("2026-09-24", "브랜드 방어",   1, 0,     0, 0, 0),
]

METRICS = [("CTR","클릭 ÷ 노출","5% 이상 양호. 브랜드 키워드는 15%도 나옵니다"),
 ("평균 CPC","비용 ÷ 클릭","설정 상한 1,500 / 2,500 / 2,000원보다 낮아야 정상"),
 ("CPA","비용 ÷ 전환","주문 1건을 따오는 데 든 광고비"),
 ("ROAS","전환값 ÷ 비용","1배는 본전. 3배 이상이어야 남는 장사"),
 ("전환율","전환 ÷ 클릭","사이트 평균이 1.2% 수준이니 그 근처면 정상")]

TODO = [
 ("위험", "검색 파트너 네트워크를 끄셔야 합니다 — 오늘만 3.2만원",
  "9/24~9/25 이틀간 <b>검색 파트너</b>(구글 검색이 아닌 제휴 사이트)에서 클릭 373건 · "
  "40,709원이 나갔습니다. CTR 26~44%(정상 1.6%), CPC 101~293원, 100% 모바일 — "
  "사람이 실제로 누른 트래픽이 아닙니다. 구글의 무효클릭 필터는 3.5%만 걸러냈습니다. "
  "<b>구글애드 UI → 캠페인 선택 → 설정 → 네트워크 → 「Google 검색 파트너 포함」 체크 해제</b>. "
  "붓기·칼륨 두 캠페인 모두. API에 이 설정을 바꾸는 기능이 없어 제가 못 합니다."),
 ("위험", "확장검색 키워드 3개가 이 누수의 통로다 — 중지 결정 필요",
  "9/24~25 낭비 클릭은 전부 <b>「칼륨 영양제」(확장) · 「붓기 영양제」(확장) · 「붓기 칼륨」(확장)</b> "
  "3개에서 나왔습니다. 9/24 칼륨 영양제(확장) 56클릭 15,012원, 9/25 붓기 영양제(확장) 137클릭 "
  "13,879원 + 칼륨 영양제(확장) 178클릭 18,434원. 합 <b>47,431원</b>. "
  "9/22~23에는 이 3개가 0원이었는데 구글이 이틀 만에 확장 범위를 넓혔습니다. "
  "제외 키워드는 사후 대응이라 계속 새 단어가 나옵니다. <b>3개 일시중지</b>를 권합니다. "
  "말씀만 주시면 1분입니다."),
 ("위험", "잘못 만들어진 스니펫 삭제",
  "브랜드 방어 캠페인 → 애셋 → 구조화된 스니펫에서 <code>423881840386</code> 을 지우세요. 값이 "
  "<b>비타민B오플렉스</b>로 잘못 들어갔습니다. 제가 API로는 삭제할 수 없습니다. "
  "올바른 것(<code>423782247365</code>)은 이미 등록돼 있습니다."),
 ("위험", "정보 검색이 광고비를 다 쓰고 있다 — 키워드 결정 필요",
  "9/23~9/24 과금된 검색어를 전부 확인했습니다. <b>확장검색이 아니라 우리가 고른 구문검색 키워드</b>가 "
  "원인입니다. 「붓기 빼는 법」이 <b>붓기 빼는 방법</b>(1,741원)을, 「붓기 차」가 <b>붓기 빼는 차·부종에 좋은 차·"
  "호박 차 추천</b>(5,190원)을 끌어옵니다. 제외 키워드로는 막을 수 없습니다 — 막으면 그 키워드 자체가 죽습니다. "
  "<b>「붓기 빼는 법」·「붓기 제거」·「붓기 차」 3개 제거</b>가 근본 해결이고, 캠페인 구조 변경이라 대표님 결정이 필요합니다."),
 ("정리", "제외 키워드가 실제로 작동하고 있다",
  "9/23에는 <b>음식·약·호박</b> 검색어로 7,831원이 과금됐는데, 제외 키워드 40개를 넣은 뒤인 <b>9/24에는 "
  "같은 유형이 0건</b>입니다. 9/24 신규 누수(찜질·무릎·파인셔스)도 오늘 31개를 추가해 막았습니다. "
  "붓기 캠페인 제외 키워드는 이제 <b>102개</b>입니다."),
 ("주의", "근거를 확인하지 못한 문안 2종",
  "<b>재구매율 92%</b>(브랜드 광고 제목 7)와 <b>14개국 수출</b>(브랜드 광고 설명 3)은 제가 뒷받침 데이터를 "
  "본 적이 없습니다. 심의에서 증빙을 요구할 수 있습니다."),
 ("주의", "붓기·칼륨 광고에 「후기 333건」이 남아 있다",
  "브랜드 광고에서는 대표님 지시로 삭제했지만 <code>825526179099</code>(붓기)와 "
  "<code>825649070789</code>(칼륨)에는 그대로 있습니다. 두 광고는 칼륨 상세페이지로 보내므로 333건이 "
  "사실과 맞습니다. 삭제 여부 확인 대기 중입니다."),
 ("주의", "심의 비승인 가능 문안 2종",
  "<b>설인아 PICK 젠제네틱스</b>는 유명인 이름, <b>올리브영·쿠팡 1위</b>는 최상급 표현입니다. "
  "반응형 검색광고는 문안 하나씩 심의되니 한 개가 걸려도 광고 전체는 계속 나갑니다."),
 ("정리", "중복 광고 2개 삭제(선택)",
  "<code>199923244786~825567922000</code> / <code>207170880944~825525918138</code> — 최종 URL "
  "슬러그 오타로 만들었다가 교체한 것입니다. 이미 일시중지 상태이니 지워도 무해합니다."),
]
SETUP = [
 "Windsor.ai의 <b>google_ads 커넥터</b>로 Google Ads API를 직접 호출해 만들었습니다. UI 마법사를 쓰지 않았습니다.",
 "처음 열려 있던 <b>실적 최대화(Performance Max)</b> 캠페인은 폐기했습니다 — 키워드를 지정할 수 없어 "
 "붓기·칼륨·젠제네틱스 타겟이 원리적으로 불가능합니다.",
 "캠페인 3 · 광고그룹 3 · 광고 3 · 키워드 42 · 제외 키워드 121+ · 광고 확장 30 · 위치 · 언어 · 입찰을 모두 API로 설정했습니다.",
 "전부 일시중지로 만든 뒤 전환 추적과 결제를 마치고 게재를 시작했습니다.",
 "등록한 키워드 42개는 등록 후 <b>다시 읽어</b> 한글이 깨지지 않았음을 확인했습니다.",
]

def glen(s): return sum(2 if ud.east_asian_width(c) in ("W","F") else 1 for c in str(s))
def won(n): return f"{n:,}"
def e(s):   return html.escape(str(s))

# ── 차트 (정적 SVG, 수치는 여기서 계산) ────────────────────────────────
def revenue_chart():
    W, H = 780, 286
    L, R, T = 62, 14, 18
    BASE_Y = 208                       # x축
    TOP_V  = 3_000_000
    plot_h = BASE_Y - T
    band = (W - L - R) / len(GA4)
    bw = min(28, band * 0.56)
    avg = sum(v for _,_,_,v in GA4[:BASE_N]) / BASE_N

    def y(v): return BASE_Y - v / TOP_V * plot_h

    p = []
    p.append(f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
             f'aria-label="GA4 일별 매출 막대 그래프. 9월 9일부터 22일까지." '
             f'preserveAspectRatio="xMidYMid meet">')
    # 격자 + y 라벨
    for v, lab in [(0,"0"),(1_000_000,"100만"),(2_000_000,"200만"),(3_000_000,"300만")]:
        yy = y(v)
        p.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{yy+3.5:.1f}" class="ytick" text-anchor="end">{lab}</text>')
    # 평균선
    ay = y(avg)
    p.append(f'<line x1="{L}" y1="{ay:.1f}" x2="{W-R}" y2="{ay:.1f}" class="avgline"/>')
    p.append(f'<rect x="{W-R-104}" y="{ay-19:.1f}" width="104" height="15" rx="3" class="avgchip"/>')
    p.append(f'<text x="{W-R-52}" y="{ay-8:.1f}" class="avglab" text-anchor="middle">'
             f'광고 전 평균 {round(avg/10000):,}만원</text>')
    # 막대
    for i, (d, s, t, v) in enumerate(GA4):
        cx = L + band * (i + .5)
        yy = y(v); h = BASE_Y - yy
        cls = "bar"
        if d == "2026-09-21": cls = "bar warnbar"
        if d == GA4[-1][0]:   cls = "bar partbar"   # 마지막 날은 항상 집계 진행 중
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{max(h,1.5):.1f}" rx="2" class="{cls}"/>')
        p.append(f'<text x="{cx:.1f}" y="{BASE_Y+15:.1f}" class="xtick" text-anchor="middle">{d[5:]}</text>')
        p.append(f'<text x="{cx:.1f}" y="{BASE_Y+31:.1f}" class="xcount" text-anchor="middle">{t}</text>')
    p.append(f'<line x1="{L}" y1="{BASE_Y}" x2="{W-R}" y2="{BASE_Y}" class="axis"/>')
    p.append(f'<text x="{L-10}" y="{BASE_Y+31:.1f}" class="rowlab" text-anchor="end">거래수</text>')
    p.append(f'<text x="{L}" y="{H-6}" class="foot">막대 = 일 매출 (원)  ·  아래 숫자 = 그날 거래 건수</text>')
    p.append('</svg>')
    return "\n".join(p)

# ── 페이지 ──────────────────────────────────────────────────────────────
avg_tx  = sum(t for _,_,t,_ in GA4[:BASE_N]) / BASE_N
avg_rev = sum(v for _,_,_,v in GA4[:BASE_N]) / BASE_N
avg_ses = sum(s for _,s,_,_ in GA4[:BASE_N]) / BASE_N
aov     = avg_rev / avg_tx

o = io.StringIO()
w = o.write

w('<title>젠제네틱스 검색광고 콘솔</title>\n')
w('<link rel="preconnect" href="https://fonts.googleapis.com">\n')
w('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n')
w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
  'family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">\n')

w('''<style>
:root{
  --ground:#F6F9FA; --surface:#FFFFFF; --surface-2:#EFF4F5;
  --ink:#152329; --ink-2:#3D565F; --muted:#6C838C; --line:#DBE4E7; --line-2:#C7D4D8;
  --accent:#0F6E6E; --accent-ink:#0B5252; --accent-soft:#E2EFEE;
  --good:#1B7F4B; --good-soft:#E3F1E9;
  --warn:#9A5B00; --warn-soft:#F6EBD9;
  --crit:#A82318; --crit-soft:#F7E4E1;
  --shadow:0 1px 2px rgba(21,35,41,.05), 0 6px 20px -12px rgba(21,35,41,.18);
  --mono:'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --sans:'IBM Plex Sans KR', system-ui, -apple-system, 'Apple SD Gothic Neo', sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0D1518; --surface:#152126; --surface-2:#1C2B31;
    --ink:#E7EFF1; --ink-2:#BACAD0; --muted:#8CA2AA; --line:#28393F; --line-2:#374C53;
    --accent:#4FB3AA; --accent-ink:#7FCCC4; --accent-soft:#16332F;
    --good:#5FC189; --good-soft:#16301F;
    --warn:#D79B45; --warn-soft:#332616;
    --crit:#E8857A; --crit-soft:#331C19;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -14px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#0D1518; --surface:#152126; --surface-2:#1C2B31;
  --ink:#E7EFF1; --ink-2:#BACAD0; --muted:#8CA2AA; --line:#28393F; --line-2:#374C53;
  --accent:#4FB3AA; --accent-ink:#7FCCC4; --accent-soft:#16332F;
  --good:#5FC189; --good-soft:#16301F;
  --warn:#D79B45; --warn-soft:#332616;
  --crit:#E8857A; --crit-soft:#331C19;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -14px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
     font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px;padding-block:0 64px}

/* ── 헤더 ── */
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;
     background:color-mix(in srgb, var(--ground) 88%, transparent);
     backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1040px;margin:0 auto;padding:12px 16px;display:flex;flex-wrap:wrap;
        gap:10px 18px;align-items:baseline}
.brand{font-weight:700;font-size:16px;letter-spacing:-.01em}
.brand span{color:var(--accent);font-weight:600}
.meta{font-family:var(--mono);font-size:11.5px;color:var(--muted);display:flex;flex-wrap:wrap;gap:14px}
.live{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:12px;
      font-weight:600;color:var(--good);background:var(--good-soft);
      border:1px solid color-mix(in srgb, var(--good) 30%, transparent);
      border-radius:999px;padding:3px 11px 3px 8px;white-space:nowrap}
.dot{width:7px;height:7px;border-radius:50%;background:var(--good);flex:none}

/* ── 섹션 ── */
section{padding-block:34px 0}
.sec-h{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
       border-bottom:1px solid var(--line);padding-bottom:9px;margin-bottom:18px}
h2{margin:0;font-size:17px;font-weight:600;letter-spacing:-.01em;text-wrap:balance}
.sec-n{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto}
.sec-d{margin:-8px 0 18px;color:var(--ink-2);max-width:66ch}

/* ── 알림 ── */
.note{display:flex;gap:13px;background:var(--surface);border:1px solid var(--line);
      border-left:3px solid var(--accent);border-radius:4px;padding:15px 17px;
      margin-top:22px;box-shadow:var(--shadow)}
.note b{color:var(--ink)}
.note p{margin:0;color:var(--ink-2)}
.note .ic{font-family:var(--mono);font-weight:600;color:var(--accent);flex:none;font-size:13px}

/* ── 표 ── */
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{text-align:left;font-weight:600;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;
   color:var(--muted);padding:0 12px 8px 0;white-space:nowrap;border-bottom:1px solid var(--line-2)}
td{padding:11px 12px 11px 0;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
.num{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
th.num{text-align:right}
.tot td{border-top:1px solid var(--line-2);border-bottom:0;font-weight:600;
        background:var(--surface-2)}
.cid{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.cname{font-weight:600}
.why{color:var(--ink-2);font-size:12.5px;max-width:40ch}

/* 예산 배분 바 */
.bbar{height:5px;border-radius:3px;background:var(--surface-2);overflow:hidden;
      min-width:64px;margin-top:6px}
.bbar i{display:block;height:100%;background:var(--accent);border-radius:3px}

/* ── 통계 행 ── */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:1px;
       background:var(--line);border:1px solid var(--line);border-radius:5px;overflow:hidden}
.stat{background:var(--surface);padding:15px 16px}
.stat dt{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);
         font-weight:600;margin-bottom:5px}
.stat dd{margin:0;font-family:var(--mono);font-size:21px;font-weight:600;letter-spacing:-.02em;
         font-variant-numeric:tabular-nums}
.stat dd small{font-family:var(--sans);font-size:12px;font-weight:400;color:var(--muted);
               margin-left:3px;letter-spacing:0}

/* ── 차트 ── */
.chartbox{margin-top:20px;background:var(--surface);border:1px solid var(--line);
          border-radius:5px;padding:18px 14px 8px;box-shadow:var(--shadow)}
.chart{width:100%;height:auto;display:block;font-family:var(--mono)}
.chart .grid{stroke:var(--line);stroke-width:1}
.chart .axis{stroke:var(--line-2);stroke-width:1}
.chart .bar{fill:var(--accent)}
.chart .warnbar{fill:var(--warn)}
.chart .partbar{fill:var(--line-2)}
.chart .ytick,.chart .xtick{fill:var(--muted);font-size:10px}
.chart .xcount{fill:var(--ink-2);font-size:10px;font-weight:600}
.chart .rowlab{fill:var(--muted);font-size:9.5px;font-family:var(--sans)}
.chart .foot{fill:var(--muted);font-size:10px;font-family:var(--sans)}
.chart .avgline{stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 3}
.chart .avgchip{fill:var(--surface);stroke:var(--line-2)}
.chart .avglab{fill:var(--ink-2);font-size:9.5px;font-family:var(--sans)}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);
        margin-top:10px;padding-left:2px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px}

/* ── 키워드 ── */
.kwgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(272px,1fr));gap:18px}
.kwcol h3{margin:0 0 3px;font-size:13.5px;font-weight:600}
.kwcol .cnt{font-family:var(--mono);font-size:11px;color:var(--muted);margin-bottom:9px}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font-size:12.5px;padding:3px 9px;border-radius:3px;background:var(--surface);
      border:1px solid var(--line);white-space:nowrap}
.chip.exact{border-color:var(--accent);color:var(--accent-ink);font-weight:500;
            background:var(--accent-soft)}
.chip.broad{border-color:color-mix(in srgb, var(--warn) 45%, transparent);
            background:var(--warn-soft);color:var(--warn);font-weight:500}
.mt{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-bottom:16px}
.mt b{color:var(--ink-2);font-weight:600}

/* ── 제외 키워드 ── */
.neg{display:grid;grid-template-columns:repeat(auto-fit,minmax(228px,1fr));gap:14px 22px}
.neggrp dt{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:600;
           color:var(--muted);margin-bottom:6px}
.neggrp.hot dt{color:var(--crit)}
.neggrp dd{margin:0;display:flex;flex-wrap:wrap;gap:4px}
.nchip{font-size:12px;padding:2px 7px;border-radius:3px;background:var(--surface-2);
       color:var(--ink-2);border:1px solid transparent}
.neggrp.hot .nchip{background:var(--crit-soft);color:var(--crit);
                   border-color:color-mix(in srgb, var(--crit) 22%, transparent)}

/* ── 문안 ── */
.copy{display:grid;gap:22px}
.cgrp h3{margin:0 0 10px;font-size:13.5px;font-weight:600;display:flex;gap:9px;align-items:baseline}
.cgrp h3 em{font-style:normal;font-family:var(--mono);font-size:11px;color:var(--muted)}
.lines{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:4px;
       overflow:hidden}
.line{background:var(--surface);display:grid;grid-template-columns:22px 1fr 88px;
      gap:10px;align-items:center;padding:8px 13px}
.line .i{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:right}
.line .t{font-size:13px}
.gauge{display:flex;align-items:center;gap:7px;justify-content:flex-end}
.gauge b{font-family:var(--mono);font-size:11px;font-weight:500;color:var(--muted);
         font-variant-numeric:tabular-nums}
.gbar{width:38px;height:4px;border-radius:2px;background:var(--surface-2);overflow:hidden;flex:none}
.gbar i{display:block;height:100%;background:var(--accent)}
.gbar.tight i{background:var(--warn)}

/* ── 할 일 ── */
.todo{display:grid;gap:11px}
.item{display:grid;grid-template-columns:auto 1fr;gap:13px;background:var(--surface);
      border:1px solid var(--line);border-radius:4px;padding:14px 16px}
.item.crit{border-left:3px solid var(--crit)}
.item.warn{border-left:3px solid var(--warn)}
.item.info{border-left:3px solid var(--line-2)}
.sev{font-size:11px;font-weight:700;letter-spacing:.04em;padding:2px 8px;border-radius:3px;
     height:fit-content;white-space:nowrap}
.sev.crit{background:var(--crit-soft);color:var(--crit)}
.sev.warn{background:var(--warn-soft);color:var(--warn)}
.sev.info{background:var(--surface-2);color:var(--muted)}
.item h4{margin:0 0 3px;font-size:13.5px;font-weight:600}
.item p{margin:0;color:var(--ink-2);font-size:13px}
code{font-family:var(--mono);font-size:.9em;background:var(--surface-2);padding:1px 5px;
     border-radius:3px;color:var(--ink-2)}

/* ── 정의 목록 ── */
.kv{display:grid;grid-template-columns:auto 1fr;gap:9px 20px;font-size:13.5px}
.kv dt{font-weight:600;white-space:nowrap;color:var(--ink)}
.kv dd{margin:0;color:var(--ink-2)}
ul.plain{margin:0;padding-left:19px;color:var(--ink-2);display:grid;gap:7px;max-width:82ch}
ul.plain li::marker{color:var(--accent)}

/* ── 비어있는 표 ── */
.empty{background:var(--surface);border:1px dashed var(--line-2);border-radius:5px;
       padding:26px 20px;text-align:center;color:var(--ink-2)}
.empty strong{display:block;color:var(--ink);font-size:14.5px;margin-bottom:5px}

footer{margin-top:46px;padding-top:20px;border-top:1px solid var(--line);
       color:var(--muted);font-size:12px;display:flex;flex-wrap:wrap;gap:6px 20px}
footer code{background:none;padding:0}
@media (max-width:560px){
  .line{grid-template-columns:20px 1fr;gap:8px}
  .gauge{grid-column:1/-1;justify-content:flex-start;padding-left:28px}
  .stat dd{font-size:19px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
''')

# ── 헤더 ──
w('<div class="top"><div class="top-in">')
w('<div class="brand">젠제네틱스 <span>검색광고</span></div>')
w(f'<div class="meta"><span>계정 {ACCOUNT}</span><span>KRW</span>'
  f'<span>게재 시작 {START}</span></div>')
w('<div class="live"><i class="dot"></i>캠페인 3개 게재중</div>')
w('</div></div>\n')

w('<div class="wrap">\n')

# ── 알림 ──
w('<div class="note" style="border-left-color:var(--crit)">'
  '<span class="ic" style="color:var(--crit)">!</span><div>'
  '<p><b>지금 광고비가 검색 파트너 사이트로 새고 있습니다. 오늘 오전에만 32,419원.</b> '
  '9/25 오전 9시 38분 기준 클릭 316건 중 <b>314건(99%)이 구글 검색이 아니라 '
  '「검색 파트너」 사이트</b>에서 나왔습니다. CTR이 26~44%(정상 1.6%), CPC는 101원까지 '
  '떨어졌고, 전부 모바일입니다. 검색어는 「건강보조식품」·「건강기능식품」 같은 '
  '<b>우리 제품과 무관한 일반어</b>입니다. '
  '제외 키워드 19개를 두 캠페인에 즉시 넣어 오늘 낭비의 약 73%를 막았지만, '
  '<b>근본 원인은 검색 파트너 네트워크 + 확장검색 키워드 3개</b>이고 이건 '
  '대표님이 결정하셔야 합니다. 아래 「지금 손봐야 할 것」 첫 항목을 보세요.</p>'
  '<p style="margin-top:8px">한편 <b>9/24에 첫 전환 1건(38,400원)</b>이 붓기 캠페인에서 '
  '잡혔습니다.</p></div></div>\n')

# ── 1. 캠페인 ──
w('<section><div class="sec-h"><h2>캠페인</h2>'
  f'<span class="sec-n">일 예산 합계 {won(TOTAL_BUDGET)}원 · 월 약 120만원</span></div>')
w('<p class="sec-d">키워드 성격이 달라서 셋을 따로 굴립니다. 한 캠페인에 몰면 '
  '싼 브랜드 검색과 비싼 일반 검색이 예산을 서로 잡아먹습니다.</p>')
w('<div class="scroll"><table><thead><tr>'
  '<th>캠페인</th><th>역할</th><th class="num">일 예산</th><th class="num">CPC 상한</th>'
  '<th class="num">키워드</th><th class="num">문안</th></tr></thead><tbody>')
for short, full, cid, bud, ceil, nkw, why in CAMPAIGNS:
    pct = bud / TOTAL_BUDGET * 100
    w('<tr>')
    w(f'<td><div class="cname">{e(short)}</div><div class="cid">{e(full)}</div>'
      f'<div class="cid">{cid}</div></td>')
    w(f'<td class="why">{e(why)}</td>')
    w(f'<td class="num">{won(bud)}원<div class="bbar"><i style="width:{pct:.0f}%"></i></div></td>')
    w(f'<td class="num">{won(ceil)}원</td>')
    w(f'<td class="num">{nkw}</td>')
    w(f'<td class="num">제목 {len(HL[short])}<br>설명 {len(DS[short])}</td>')
    w('</tr>')
w(f'<tr class="tot"><td>합계</td><td></td><td class="num">{won(TOTAL_BUDGET)}원</td>'
  f'<td class="num">—</td><td class="num">42</td><td class="num">—</td></tr>')
w('</tbody></table></div>')
w('<div class="stats" style="margin-top:18px">')
for dt_, dd_, sm in [("위치","대한민국",""),("언어","한국어 + 영어",""),
                     ("입찰","클릭수 최대화",""),("캠페인 유형","검색","Search")]:
    w(f'<div class="stat"><dt>{dt_}</dt><dd style="font-size:15px;font-family:var(--sans)">'
      f'{e(dd_)}{f" <small>{sm}</small>" if sm else ""}</dd></div>')
w('</div>')
w('<p class="sec-d" style="margin-top:14px;margin-bottom:0">언어를 <b>한국어만</b> 걸면 안 됩니다. '
  '구글의 언어 타겟팅은 검색어 언어가 아니라 <b>사용자의 브라우저·구글 인터페이스 언어</b> 기준이라, '
  '크롬을 영문으로 쓰는 국내 사용자가 「붓기」를 한글로 검색해도 광고가 안 나갑니다.</p>')
w('</section>\n')

# ── 2. 일별 실적 ──
w('<section><div class="sec-h"><h2>일별 실적</h2>'
  '<span class="sec-n">매일 갱신</span></div>')
if DAILY:
    w('<div class="scroll"><table><thead><tr><th>날짜</th><th>캠페인</th>'
      '<th class="num">노출</th><th class="num">클릭</th><th class="num">CTR</th>'
      '<th class="num">평균 CPC</th><th class="num">비용</th><th class="num">전환</th>'
      '<th class="num">전환값</th><th class="num">CPA</th><th class="num">ROAS</th>'
      '</tr></thead><tbody>')
    for d, camp, imp, clk, cost, conv, cval in DAILY:
        ctr = clk/imp if imp else 0
        cpc = cost/clk if clk else 0
        cpa = cost/conv if conv else 0
        roas = cval/cost if cost else 0
        w(f'<tr><td class="num" style="text-align:left">{d}</td><td>{e(camp)}</td>'
          f'<td class="num">{won(imp)}</td><td class="num">{won(clk)}</td>'
          f'<td class="num">{ctr*100:.2f}%</td><td class="num">{won(round(cpc))}원</td>'
          f'<td class="num">{won(cost)}원</td><td class="num">{conv}</td>'
          f'<td class="num">{won(cval)}원</td><td class="num">{won(round(cpa))}원</td>'
          f'<td class="num">{roas:.2f}배</td></tr>')
    w('</tbody></table></div>')
else:
    w('<div class="empty"><strong>아직 실적이 없습니다</strong>'
      f'{START} 게재 시작 · 심의 통과 후 집계됩니다. 매일 제가 조회해 이 표를 채웁니다.</div>')
w('<div class="sec-h" style="margin-top:28px"><h2 style="font-size:14px">지표를 어떻게 읽나</h2></div>')
w('<div class="scroll"><table><thead><tr><th>지표</th><th>계산</th><th>판단 기준</th>'
  '</tr></thead><tbody>')
for a, b, c in METRICS:
    w(f'<tr><td><b>{e(a)}</b></td><td class="cid" style="font-size:12.5px">{e(b)}</td>'
      f'<td class="why" style="max-width:52ch">{e(c)}</td></tr>')
w('</tbody></table></div></section>\n')

# ── 3. 기준선 ──
w('<section><div class="sec-h"><h2>광고 켜기 전 기준선</h2>'
  '<span class="sec-n">GA4 · 2026-09-09 ~ 09-25</span></div>')
w('<p class="sec-d">광고가 효과 있었는지는 <b>광고 켜기 전 매출</b>과 비교해야 알 수 있습니다. '
  '구글애드가 「전환 5건」이라고 해도 전체 매출이 그대로면, 원래 살 사람에게 돈 주고 광고를 보여준 것입니다.</p>')
w('<div class="stats">')
for dt_, val, sm in [("일 세션", won(round(avg_ses)), ""),
                     ("일 거래수", f"{avg_tx:.1f}", "건"),
                     ("일 매출", won(round(avg_rev)), "원"),
                     ("객단가", won(round(aov)), "원")]:
    w(f'<div class="stat"><dt>{dt_}</dt><dd>{val}<small>{sm}</small></dd></div>')
w('</div>')
w('<div class="chartbox">')
w(revenue_chart())
w('<div class="legend">'
  '<span><i style="background:var(--accent)"></i>일 매출</span>'
  '<span><i style="background:var(--warn)"></i>9/21 이상치 — 세션도 최저(753). 재조회해도 같음</span>'
  f'<span><i style="background:var(--line-2)"></i>{GA4[-1][0][5:]} 집계 진행 중</span>'
  '</div></div>')
w('<p class="sec-d" style="margin-top:16px;margin-bottom:0">'
  '9월 9일부터 GA4 전자상거래가 켜져 있어서 그 전 매출은 0으로 나옵니다. 실제로 안 팔린 게 아니라 '
  '<b>측정이 없었던 것</b>입니다. 그래서 기준선은 9/9~9/20 12일치 평균을 씁니다.</p>')
w('</section>\n')

# ── 4. 키워드 ──
w('<section><div class="sec-h"><h2>키워드 42개</h2>'
  '<span class="sec-n">등록 후 다시 읽어 검증</span></div>')
w('<div class="mt">'
  '<span><b>완전일치</b> 이 검색어와 거의 똑같을 때만</span>'
  '<span><b>구문일치</b> 이 어구를 포함한 검색에</span>'
  '<span><b>확장검색</b> 관련 검색까지 폭넓게</span></div>')
w('<div class="kwgrid">')
for short, full, cid, bud, ceil, nkw, why in CAMPAIGNS:
    w('<div class="kwcol">')
    w(f'<h3>{e(short)}</h3><div class="cnt">{nkw}개</div><div class="chips">')
    for kw, mt in KW[short]:
        cls = {"완전":"chip exact","구문":"chip","확장":"chip broad"}[mt]
        suffix = {"완전":" · 완전","구문":"","확장":" · 확장"}[mt]
        w(f'<span class="{cls}">{e(kw)}{suffix}</span>')
    w('</div></div>')
w('</div>')
w('<p class="sec-d" style="margin-top:18px;margin-bottom:0">'
  '문서 원안의 변형확장(<code>+붓기 +영양제</code>)은 구글이 2021년에 폐지했으므로 확장검색으로 바꿔 넣었습니다. '
  '주황색 3건이 예산이 새는 지점이라 검색어 보고서로 매일 봐야 합니다.</p>')
w('</section>\n')

# ── 5. 제외 키워드 ──
w('<section><div class="sec-h"><h2>제외 키워드 121+개</h2>'
  '<span class="sec-n">캠페인 레벨 · 붓기 121 · 칼륨 50 · 브랜드 30</span></div>')
w('<p class="sec-d">이 단어가 든 검색에는 광고가 나가지 않습니다. 예산이 새는 걸 막는 장치입니다.</p>')
w('<div class="neg">')
for name, words, hot in NEG_GROUPS:
    w(f'<dl class="neggrp{" hot" if hot else ""}"><dt>{e(name)}</dt><dd>')
    for x in words:
        w(f'<span class="nchip">{e(x)}</span>')
    w('</dd></dl>')
w('</div>')
w('<div class="note" style="border-left-color:var(--warn)"><span class="ic" '
  'style="color:var(--warn)">※</span><div><p><b>브랜드 방어에서만 「무료」를 뺐습니다.</b> '
  '「젠제네틱스 무료배송」은 구매 직전 검색이라 막으면 손해입니다. 그래서 브랜드는 30개, '
  '붓기·칼륨은 31개입니다.</p></div></div>')
w('</section>\n')

# ── 6. 문안 ──
w('<section><div class="sec-h"><h2>광고 문안</h2>'
  f'<span class="sec-n">광고 제목 {sum(len(v) for v in HL.values())} + '
  f'설명 {sum(len(v) for v in DS.values())} · 한도 초과 0건</span></div>')
w('<p class="sec-d">구글애드는 <b>한글 1자를 2자로</b> 셉니다. 그래서 「30자」 칸은 실제로 한글 15자, '
  '「90자」 칸은 한글 45자가 한계입니다. 오른쪽 막대가 한도 대비 사용량입니다.</p>')
w('<div class="copy">')
for short, *_ in CAMPAIGNS:
    w(f'<div class="cgrp"><h3>{e(short)} <em>제목 {len(HL[short])} · '
      f'설명 {len(DS[short])}</em></h3><div class="lines">')
    for i, t in enumerate(HL[short], 1):
        L = glen(t); pct = L/30*100
        tight = " tight" if L >= 28 else ""
        w(f'<div class="line"><span class="i">{i}</span><span class="t">{e(t)}</span>'
          f'<span class="gauge"><b>{L}/30</b>'
          f'<span class="gbar{tight}"><i style="width:{pct:.0f}%"></i></span></span></div>')
    for i, t in enumerate(DS[short], 1):
        L = glen(t); pct = L/90*100
        w(f'<div class="line"><span class="i">D{i}</span><span class="t">{e(t)}</span>'
          f'<span class="gauge"><b>{L}/90</b>'
          f'<span class="gbar"><i style="width:{pct:.0f}%"></i></span></span></div>')
    w('</div></div>')
w('</div></section>\n')

# ── 7. 광고 확장 ──
w('<section><div class="sec-h"><h2>광고 확장 30개</h2>'
  '<span class="sec-n">사이트링크 12 · 콜아웃 12 · 스니펫 3 · 전화 3</span></div>')
w('<p class="sec-d">검색 결과에서 광고 아래에 같이 붙는 부가 정보입니다. 광고가 차지하는 면적이 커져서 '
  '클릭률이 올라갑니다.</p>')
w('<div class="scroll"><table><thead><tr><th>유형</th><th>내용</th><th>비고</th>'
  '</tr></thead><tbody>')
for a, b, c in EXT:
    w(f'<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td class="cid" style="font-size:12.5px">{e(c)}</td></tr>')
w('</tbody></table></div></section>\n')

# ── 8. 전환 추적 ──
w('<section><div class="sec-h"><h2>전환 추적</h2>'
  '<span class="sec-n">카페24에 코드 미설치</span></div>')
w('<dl class="kv">')
for k, v in [("방식","GA4 전환 가져오기. 카페24 상세페이지 편집기가 <code>&lt;script&gt;</code>를 지우는 문제를 원천적으로 피했습니다."),
             ("전환 액션","<code>젠제네틱스_속성 (web) purchase</code> — 1개, <b>기본 목표</b>"),
             ("GA4 속성","<code>498152534</code> · 2026-09-09부터 매출 금액까지 정상 수집"),
             ("전환 값","GA4가 보내는 실제 주문금액을 씁니다 → ROAS가 계산됩니다"),
             ("횟수 / 기간","전체 / 30일"),
             ("데이터 지연","24~48시간. 이게 GA4 가져오기 방식의 유일한 대가입니다"),
             ("gclid 유실","없음. 랜딩 3개 URL을 데스크톱·모바일로 확인 — 전부 리다이렉트 0회, 파라미터 보존"),
             ("전환으로 안 잡은 것","첫구매 페이지 방문 · <code>zg_purchase_repeat_view</code> · <code>zg_purchase_unreadable</code> · <code>add_to_cart</code> · <code>begin_checkout</code>")]:
    w(f'<dt>{k}</dt><dd>{v}</dd>')
w('</dl>')
w('<div class="note" style="margin-top:20px"><span class="ic">?</span><div><p>'
  '<b>왜 장바구니를 전환으로 안 잡나.</b> 담기만 한 사람을 전환으로 세면 숫자가 부풀고, '
  '자동입찰이 「담고 안 사는 사람」을 열심히 데려옵니다. 광고비 대비 전환은 좋아 보이는데 '
  '매출은 안 늘어나는 최악의 상태가 됩니다.</p></div></div>')
w('</section>\n')

# ── 9. 할 일 ──
w('<section><div class="sec-h"><h2>지금 손봐야 할 것</h2></div>')
w('<div class="todo">')
SEVCLS = {"위험":"crit","주의":"warn","정리":"info"}
for sev, title, body in TODO:
    c = SEVCLS[sev]
    w(f'<div class="item {c}"><span class="sev {c}">{sev}</span>'
      f'<div><h4>{e(title)}</h4><p>{body}</p></div></div>')
w('</div></section>\n')

# ── 10. 세팅 방법 ──
w('<section><div class="sec-h"><h2>어떻게 만들었나</h2></div>')
w('<ul class="plain">')
for s in SETUP:
    w(f'<li>{s}</li>')
w('</ul>')
w('<div class="stats" style="margin-top:20px">')
for dt_, dd_ in [("결제 방식","후불"),("결제 수단","국민 ••••1880"),
                 ("청구 기준액","600,000원"),("지급인","주식회사 위스팟바이오랩")]:
    w(f'<div class="stat"><dt>{dt_}</dt>'
      f'<dd style="font-size:14px;font-family:var(--sans)">{e(dd_)}</dd></div>')
w('</div></section>\n')

w(f'<footer><span>젠제네틱스 검색광고 콘솔</span><span>계정 {ACCOUNT}</span>'
  f'<span>작성 {GEN}</span><span>실적이 쌓이면 갱신됩니다</span></footer>\n')
w('</div>\n')

open("/tmp/ads-console.html","w",encoding="utf-8").write(o.getvalue())
print("bytes:", len(o.getvalue()))
