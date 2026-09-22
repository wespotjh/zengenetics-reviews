# -*- coding: utf-8 -*-
"""구글애드 운영 보고서 생성 (xlsx → 구글 시트 변환 업로드용).

일별 실적은 Windsor.ai google_ads 커넥터에서 조회한 값을 DAILY 에 넣고 다시 실행한다.
"""
import unicodedata as ud
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ACCOUNT = "798-667-9268"
CURRENCY = "KRW"

CAMPAIGNS = [
    # 이름, 캠페인ID, 광고그룹, 광고그룹ID, 일예산, CPC상한, 광고ID, 최종URL
    ("젠제네틱스_브랜드방어_검색", "24281447473", "브랜드_전체", "204263447190", 10000, 1500,
     "204263447190~825648436268", "https://zengenetics.co.kr/"),
    ("젠제네틱스_붓기_검색", "24270384426", "붓기_일반", "199923244786", 20000, 2500,
     "199923244786~825526179099", "https://zengenetics.co.kr/product/…포타슘-칼륨-20ea/11/"),
    ("젠제네틱스_칼륨_검색", "24275789225", "칼륨_일반", "207170880944", 10000, 2000,
     "207170880944~825649070789", "https://zengenetics.co.kr/product/…포타슘-칼륨-20ea/11/"),
]

KEYWORDS = [
    ("브랜드방어", "젠제네틱스", "EXACT"), ("브랜드방어", "젠제네틱스", "PHRASE"),
    ("브랜드방어", "젠제네틱스 칼륨", "PHRASE"), ("브랜드방어", "젠제네틱스 붓기", "PHRASE"),
    ("브랜드방어", "젠제네틱스 후기", "PHRASE"), ("브랜드방어", "젠제네틱스 공식몰", "PHRASE"),
    ("브랜드방어", "젠제네틱스 마그네슘", "PHRASE"), ("브랜드방어", "젠제네틱스 비타민B", "PHRASE"),
    ("브랜드방어", "젠제네틱스 붓기파우더", "PHRASE"),
    ("브랜드방어", "zengenetics", "EXACT"), ("브랜드방어", "zengenetics", "PHRASE"),
    ("브랜드방어", "zen genetics", "PHRASE"), ("브랜드방어", "zengenetic", "PHRASE"),
    ("브랜드방어", "zengenetics korea", "PHRASE"), ("브랜드방어", "zengenetics official", "PHRASE"),
    ("브랜드방어", "위스팟바이오랩", "PHRASE"), ("브랜드방어", "wespot biolab", "PHRASE"),
    ("붓기", "붓기 영양제", "PHRASE"), ("붓기", "붓기 제거", "PHRASE"),
    ("붓기", "붓기 빼는 법", "PHRASE"), ("붓기", "붓기파우더", "PHRASE"),
    ("붓기", "붓기 보조제", "PHRASE"), ("붓기", "얼굴 붓기", "PHRASE"),
    ("붓기", "다리 붓기", "PHRASE"), ("붓기", "종아리 붓기", "PHRASE"),
    ("붓기", "아침 붓기", "PHRASE"), ("붓기", "붓기 차", "PHRASE"),
    ("붓기", "부종 영양제", "PHRASE"), ("붓기", "수분 배출", "PHRASE"),
    ("붓기", "붓기 영양제", "BROAD"), ("붓기", "붓기 칼륨", "BROAD"),
    ("칼륨", "칼륨 영양제", "PHRASE"), ("칼륨", "칼륨 보충제", "PHRASE"),
    ("칼륨", "포타슘 영양제", "PHRASE"), ("칼륨", "구연산 칼륨", "PHRASE"),
    ("칼륨", "칼륨 파우더", "PHRASE"), ("칼륨", "칼륨 스틱", "PHRASE"),
    ("칼륨", "potassium 영양제", "PHRASE"), ("칼륨", "칼륨 효능", "PHRASE"),
    ("칼륨", "칼륨 부족", "PHRASE"), ("칼륨", "전해질 영양제", "PHRASE"),
    ("칼륨", "칼륨 영양제", "BROAD"),
]

NEG_ALL = ["무료","공짜","부작용","후유증","소송","리콜","환불","해지","알바","채용","구인","연봉",
           "주가","상장","도매","총판","대리점","제조사","OEM","ODM","레시피","만들기","DIY",
           "병원","처방","약국","의약품","이뇨제","다이어트약","토렌트","중고"]

HEADLINES = {
"브랜드방어": ["젠제네틱스 공식몰","젠제네틱스 붓기파우더","붓기파우더 공식 판매처","젠제네틱스 칼륨 525mg",
 "올리브영 건강식품 1위","쿠팡 붓기 검색 1위","후기 333건 평점 4.77","재구매율 92%",
 "설인아 PICK 젠제네틱스","물없이 3초 분말스틱","독일 구연산 칼륨 원료","공식몰 최저가 구매",
 "젠제네틱스 Zengenetics 공식몰","무료배송 당일출고","생애 첫 구매 특가"],
"붓기": ["붓기파우더 젠제네틱스","붓기 영양제 칼륨","아침 얼굴 저녁 종아리","짠 음식 즐기는 분께",
 "칼륨 525mg 1일 2포","물없이 먹는 분말스틱","쿠팡 붓기 검색 1위","올리브영 건강식품 1위",
 "후기 333건 4.77점","독일 구연산 칼륨","칼륨 단일 설계","하루 2포 간편 루틴",
 "공식몰에서 구매","첫 구매 특가 확인","무료배송"],
"칼륨": ["칼륨 영양제 525mg","구연산 칼륨 1포 262mg","칼륨 1일기준치 15%","독일 Jungbunzlauer",
 "칼륨 단일 원료 설계","분말스틱 물없이 섭취","젠제네틱스 포타슘","칼륨 보충 하루 2포",
 "후기 333건 평점 4.77","올리브영 건강식품 1위","쿠팡 붓기 검색 1위","EP USP FCC 기준 충족",
 "공식몰 구매하기","무료배송 당일출고","첫 구매 특가"],
}
DESCRIPTIONS = {
"브랜드방어": ["젠제네틱스 공식몰입니다. 칼륨·마그네슘·비타민B 정품만 판매합니다.",
 "구매 후기 333건 평균 4.77점. 재구매율 92%. 공식몰에서 확인하세요.",
 "올리브영 건강식품 실시간 랭킹 1위 기록. 무료배송·당일출고.",
 "비공식 판매처 구입 시 품질 보상이 불가합니다. 공식몰에서 구매하세요."],
"붓기": ["칼륨 525mg 하루 2포. 물 없이 먹는 분말스틱으로 간편하게 챙기세요.",
 "쿠팡 붓기 검색 1위·올리브영 건강식품 1위. 후기 333건 4.77점.",
 "독일 Jungbunzlauer 구연산 칼륨 단일 설계. 1포당 칼륨 262.5mg.",
 "생애 첫 구매 특가 진행 중. 데이팩 6포로 가볍게 시작해보세요."],
"칼륨": ["1포당 구연산 칼륨 262.5mg, 2포 525mg으로 1일 기준치의 15%입니다.",
 "독일 Jungbunzlauer 원료. EP·USP·FCC·EU 231/2012 기준 충족.",
 "정제가 아닌 분말스틱. 물 없이 뜯어서 바로 섭취할 수 있습니다.",
 "구매 후기 333건 평균 4.77점. 공식몰에서 첫 구매 특가 확인하세요."],
}

SITELINKS = {
"브랜드방어": [("붓기 칼륨","칼륨 525mg 분말스틱","하루 2포 간편 섭취","/product/…칼륨-20ea/11/"),
  ("구매 후기","제품별 평점·후기 전체","매일 자동 갱신","https://review.zengenetics.co.kr/"),
  ("첫 구매 특가","데이팩 6포 체험 구성","ID당 1회 한정","/product/…생애-첫-구매-event/71/"),
  ("붓기 부스터 세트","칼륨 2박스+비타민B","설인아 PICK","/product/설인아-pick-…-set/63/")],
"붓기": [("붓기 칼륨","칼륨 525mg 분말스틱","하루 2포 간편 섭취","/product/…칼륨-20ea/11/"),
  ("구매 후기","제품별 평점·후기 전체","매일 자동 갱신","https://review.zengenetics.co.kr/"),
  ("첫 구매 특가","데이팩 6포 체험 구성","ID당 1회 한정","/product/…생애-첫-구매-event/71/"),
  ("붓기 부스터 세트","칼륨 2박스+비타민B","설인아 PICK","/product/설인아-pick-…-set/63/")],
"칼륨": [("붓기 칼륨","칼륨 525mg 분말스틱","하루 2포 간편 섭취","/product/…칼륨-20ea/11/"),
  ("구매 후기","제품별 평점·후기 전체","매일 자동 갱신","https://review.zengenetics.co.kr/"),
  ("첫 구매 특가","데이팩 6포 체험 구성","ID당 1회 한정","/product/…생애-첫-구매-event/71/"),
  ("마그네슘","마그네슘 400mg 127%","건강기능식품","/product/detail.html?product_no=16")],
}
CALLOUTS = {
"브랜드방어": ["무료배송","당일출고","올리브영 건강식품 1위","쿠팡 붓기 검색 1위"],
"붓기": ["무료배송","당일출고","올리브영 건강식품 1위","쿠팡 붓기 검색 1위"],
"칼륨": ["무료배송","당일출고","올리브영 건강식품 1위","후기 4.77점"],
}

GA4 = [  # 날짜, 세션, 거래수, 매출
 ("2026-09-09",1007,19,774700),("2026-09-10",1313,13,585300),("2026-09-11",1178,12,505340),
 ("2026-09-12",1597,24,2094824),("2026-09-13",932,15,1202910),("2026-09-14",934,11,1282462),
 ("2026-09-15",1304,25,2984991),("2026-09-16",1193,14,1738612),("2026-09-17",1246,11,1278524),
 ("2026-09-18",1094,11,973840),("2026-09-19",964,16,2342940),("2026-09-20",1251,19,2062900),
 ("2026-09-21",753,5,182560),("2026-09-22",469,9,895220),
]

DAILY = []  # (날짜, 캠페인, 노출, 클릭, 비용, 전환, 전환값) — 실적 생기면 채운다

# ---------- 서식 ----------
H_FILL = PatternFill("solid", fgColor="1F3864")
H_FONT = Font(color="FFFFFF", bold=True, size=10)
T_FONT = Font(bold=True, size=13, color="1F3864")
SUB    = Font(italic=True, size=9, color="808080")
WARN   = Font(bold=True, color="C00000")
OK     = Font(bold=True, color="217346")
THIN   = Border(*[Side(style="thin", color="D9D9D9")]*4)

def glen(s):
    return sum(2 if ud.east_asian_width(c) in ("W","F") else 1 for c in str(s))

def head(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.fill, cell.font = H_FILL, H_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=row+1, column=1)

def title(ws, text, sub=None):
    ws["A1"] = text; ws["A1"].font = T_FONT
    if sub:
        ws["A2"] = sub; ws["A2"].font = SUB

wb = Workbook()

# ===== 1. 요약 =====
ws = wb.active; ws.title = "요약"
title(ws, "젠제네틱스 구글 검색광고 운영 보고서",
      f"계정 {ACCOUNT} · 통화 {CURRENCY} · 게재 시작 2026-09-22 · 캠페인 유형: 검색(Search)")
head(ws, 4, ["캠페인","캠페인 ID","광고그룹","상태","일 예산","CPC 상한","입찰 전략","키워드","위치","언어"],
     [28,14,14,10,11,11,20,9,12,12])
r = 5
for name, cid, ag, agid, bud, ceil, adid, url in CAMPAIGNS:
    key = name.split("_")[1]
    n_kw = sum(1 for k in KEYWORDS if k[0] == key)
    vals = [name, cid, ag, "게재중", bud, ceil, "클릭수 최대화", n_kw, "대한민국", "한국어+영어"]
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=r, column=i, value=v)
        if i in (5, 6): c.number_format = '#,##0"원"'
        if i == 4: c.font = OK
    r += 1
ws.cell(row=r, column=1, value="합계").font = Font(bold=True)
ws.cell(row=r, column=5, value=f"=SUM(E5:E{r-1})").number_format = '#,##0"원"'
ws.cell(row=r, column=5).font = Font(bold=True)
ws.cell(row=r, column=8, value=f"=SUM(H5:H{r-1})").font = Font(bold=True)

r += 2
ws.cell(row=r, column=1, value="전환 추적").font = T_FONT; r += 1
for k, v in [("방식","GA4 전환 가져오기 (카페24에 gtag 코드 미설치)"),
             ("전환 액션","젠제네틱스_속성 (web) purchase — 1개, 기본 목표(Primary)"),
             ("GA4 속성","498152534 (젠제네틱스_속성) — 2026-09-09부터 매출 금액 수집"),
             ("전환 값","GA4에서 가져온 주문금액 사용 → ROAS 계산 가능"),
             ("횟수 / 추적기간","전체 / 30일"),
             ("데이터 지연","24~48시간 (GA4 가져오기 방식의 한계)"),
             ("gclid 유실","없음 — 랜딩 3개 URL × 데스크톱/모바일 리다이렉트 0회 검증"),
             ("제외한 전환","첫구매 페이지 방문 / zg_purchase_repeat_view / zg_purchase_unreadable / add_to_cart 등")]:
    ws.cell(row=r, column=1, value=k).font = Font(bold=True)
    ws.cell(row=r, column=2, value=v); r += 1

r += 1
ws.cell(row=r, column=1, value="예산 메모").font = T_FONT; r += 1
for v in ["일 40,000원 → 월 약 120만원 페이스",
          "청구 기준액 ₩600,000 → 약 15일마다 국민카드 ••••1880 후불 청구",
          "지급인: 주식회사 위스팟바이오랩 / Google Payments ID 9622-0485-1612-9854",
          "예산은 캠페인별 개별 예산(공유 예산 아님) — 한 캠페인이 다른 캠페인 예산을 먹지 않음"]:
    ws.cell(row=r, column=1, value="·"); ws.cell(row=r, column=2, value=v); r += 1

# ===== 2. 일별 실적 =====
ws = wb.create_sheet("일별 실적")
title(ws, "일별 실적 (캠페인 단위)",
      "2026-09-22 게재 시작. 구글애드 실적은 게재 후 집계되고, 전환은 GA4 가져오기라 24~48시간 지연됩니다.")
cols = ["날짜","캠페인","노출","클릭","CTR","평균 CPC","비용","전환","전환값","CPA","ROAS","전환율"]
head(ws, 4, cols, [12,26,10,9,9,11,12,9,13,11,9,9])
if DAILY:
    r = 5
    for d, camp, imp, clk, cost, conv, cval in DAILY:
        ws.cell(row=r, column=1, value=d); ws.cell(row=r, column=2, value=camp)
        ws.cell(row=r, column=3, value=imp); ws.cell(row=r, column=4, value=clk)
        ws.cell(row=r, column=5, value=f"=IF(C{r}=0,0,D{r}/C{r})").number_format = "0.00%"
        ws.cell(row=r, column=6, value=f"=IF(D{r}=0,0,G{r}/D{r})").number_format = '#,##0"원"'
        ws.cell(row=r, column=7, value=cost).number_format = '#,##0"원"'
        ws.cell(row=r, column=8, value=conv)
        ws.cell(row=r, column=9, value=cval).number_format = '#,##0"원"'
        ws.cell(row=r, column=10, value=f"=IF(H{r}=0,0,G{r}/H{r})").number_format = '#,##0"원"'
        ws.cell(row=r, column=11, value=f"=IF(G{r}=0,0,I{r}/G{r})").number_format = "0.00"
        ws.cell(row=r, column=12, value=f"=IF(D{r}=0,0,H{r}/D{r})").number_format = "0.00%"
        r += 1
else:
    ws.cell(row=5, column=1, value="아직 실적 데이터 없음 — 게재 시작일(2026-09-22) 당일이며, 광고 심의 통과 후 집계됩니다.").font = WARN
    ws.cell(row=6, column=1, value="CTR/평균CPC/CPA/ROAS/전환율 열은 수식으로 자동 계산되도록 설계되어 있습니다. 행이 채워지면 바로 계산됩니다.").font = SUB
    ws.cell(row=8, column=1, value="계산식 정의").font = Font(bold=True)
    for i, (k, v) in enumerate([("CTR","클릭 ÷ 노출"),("평균 CPC","비용 ÷ 클릭"),
                                ("CPA","비용 ÷ 전환"),("ROAS","전환값 ÷ 비용"),
                                ("전환율","전환 ÷ 클릭")]):
        ws.cell(row=9+i, column=1, value=k).font = Font(bold=True)
        ws.cell(row=9+i, column=2, value=v)

# ===== 3. 키워드 =====
ws = wb.create_sheet("키워드")
title(ws, f"등록 키워드 전체 ({len(KEYWORDS)}개)",
      "등록 후 구글애드에서 다시 읽어 한글 깨짐 없음을 확인한 값입니다. EXACT=완전일치, PHRASE=구문일치, BROAD=확장검색")
head(ws, 4, ["캠페인","키워드","매치타입","의미"], [16,28,12,52])
MEAN = {"EXACT":"이 검색어와 (거의) 똑같이 검색할 때만 노출",
        "PHRASE":"이 어구를 포함한 검색에 노출 (어순 유지)",
        "BROAD":"관련 검색에 폭넓게 노출 — 검색어 보고서로 감시 필요"}
r = 5
for camp, kw, mt in KEYWORDS:
    for i, v in enumerate([camp, kw, mt, MEAN[mt]], 1):
        c = ws.cell(row=r, column=i, value=v)
        if i == 3 and mt == "BROAD": c.font = WARN
    r += 1
r += 1
ws.cell(row=r, column=1, value="메모").font = Font(bold=True)
ws.cell(row=r, column=2, value="문서 원안의 변형확장(+붓기 +영양제)은 구글이 2021년에 폐지했으므로 BROAD로 변환해 등록했습니다.")
ws.cell(row=r+1, column=2, value="BROAD 3건(붓기 영양제 / 붓기 칼륨 / 칼륨 영양제)은 예산이 새기 쉬우니 검색어 보고서를 매일 확인해야 합니다.")

# ===== 4. 제외 키워드 =====
ws = wb.create_sheet("제외 키워드")
title(ws, "제외 키워드 (캠페인 레벨, 총 92개)",
      "브랜드방어 30개 · 붓기 31개 · 칼륨 31개 — 전부 BROAD(확장검색) 제외")
head(ws, 4, ["제외 키워드","브랜드방어","붓기","칼륨","제외 이유"], [16,13,10,10,44])
REASON = {"무료":"프리미엄/체험만 노리는 검색 차단","공짜":"프리미엄/체험만 노리는 검색 차단",
 "부작용":"구매 의도 낮음 + 심의 위험","후유증":"구매 의도 낮음 + 심의 위험",
 "소송":"부정 이슈 검색","리콜":"부정 이슈 검색","환불":"기존 고객 CS 검색","해지":"기존 고객 CS 검색",
 "알바":"구직 검색","채용":"구직 검색","구인":"구직 검색","연봉":"구직 검색",
 "주가":"투자 정보 검색","상장":"투자 정보 검색",
 "도매":"B2B 검색","총판":"B2B 검색","대리점":"B2B 검색","제조사":"B2B 검색","OEM":"B2B 검색","ODM":"B2B 검색",
 "레시피":"직접 만들려는 검색","만들기":"직접 만들려는 검색","DIY":"직접 만들려는 검색",
 "병원":"의약품/의료 검색 — 우리는 식품","처방":"의약품/의료 검색 — 우리는 식품","약국":"의약품/의료 검색 — 우리는 식품",
 "의약품":"★ 중요 — 우리 제품은 의약품이 아님","이뇨제":"★ 중요 — 의약품 검색, 심의 위험",
 "다이어트약":"★ 중요 — 의약품 검색, 심의 위험","토렌트":"무관한 검색","중고":"중고 거래 검색"}
r = 5
for kw in NEG_ALL:
    brand = "—" if kw == "무료" else "✔"
    for i, v in enumerate([kw, brand, "✔", "✔", REASON.get(kw, "")], 1):
        c = ws.cell(row=r, column=i, value=v)
        if i in (2,3,4): c.alignment = Alignment(horizontal="center")
        if i == 2 and brand == "—": c.font = WARN
    r += 1
r += 1
ws.cell(row=r, column=1, value="예외").font = WARN
ws.cell(row=r, column=2, value="브랜드방어 캠페인에서만 '무료'를 제외 목록에서 뺐습니다 — 「젠제네틱스 무료배송」은 구매 직전 검색이라 막으면 손해입니다.")

# ===== 5. 광고 문안 =====
ws = wb.create_sheet("광고 문안")
title(ws, "반응형 검색광고 문안 (캠페인별 광고 제목 15개 + 설명 4개)",
      "구글애드는 한글 1자를 2자로 계산합니다 → 광고 제목 한도 30(한글 15자), 설명 한도 90(한글 45자)")
head(ws, 4, ["캠페인","유형","#","문안","자수","한도","여유"], [16,11,5,58,8,8,8])
r = 5
for key in ["브랜드방어","붓기","칼륨"]:
    for i, h in enumerate(HEADLINES[key], 1):
        L = glen(h)
        for j, v in enumerate([key, "광고 제목", i, h, L, 30, 30-L], 1):
            ws.cell(row=r, column=j, value=v)
        r += 1
    for i, d in enumerate(DESCRIPTIONS[key], 1):
        L = glen(d)
        for j, v in enumerate([key, "설명", i, d, L, 90, 90-L], 1):
            ws.cell(row=r, column=j, value=v)
        r += 1
r += 1
ws.cell(row=r, column=1, value="심의 주의").font = WARN
ws.cell(row=r, column=4, value="「설인아 PICK 젠제네틱스」= 유명인 이름 / 「올리브영 건강식품 1위」「쿠팡 붓기 검색 1위」= 최상급 표현.")
ws.cell(row=r+1, column=4, value="반응형 검색광고는 애셋 단위로 비승인되므로 한 문안이 걸려도 광고 전체는 계속 게재됩니다.")

# ===== 6. 광고 확장 =====
ws = wb.create_sheet("광고 확장")
title(ws, "광고 확장 (사이트링크 12 · 콜아웃 12 · 구조화된 스니펫 3 · 전화번호 3)")
head(ws, 4, ["캠페인","유형","표시 텍스트","설명 1","설명 2 / 값","링크"], [16,16,22,24,24,46])
r = 5
for key in ["브랜드방어","붓기","칼륨"]:
    for t, d1, d2, url in SITELINKS[key]:
        for i, v in enumerate([key, "사이트링크", t, d1, d2, url], 1):
            ws.cell(row=r, column=i, value=v)
        r += 1
for key in ["브랜드방어","붓기","칼륨"]:
    for co in CALLOUTS[key]:
        for i, v in enumerate([key, "콜아웃", co, "", "", ""], 1):
            ws.cell(row=r, column=i, value=v)
        r += 1
for key in ["브랜드방어","붓기","칼륨"]:
    for i, v in enumerate([key, "구조화된 스니펫", "Types", "", "칼륨 / 마그네슘 / 비타민B컴플렉스 / 데이팩 / 세트", ""], 1):
        ws.cell(row=r, column=i, value=v)
    r += 1
for key in ["브랜드방어","붓기","칼륨"]:
    for i, v in enumerate([key, "전화번호", "070-8872-1337", "국가 KR", "", ""], 1):
        ws.cell(row=r, column=i, value=v)
    r += 1

# ===== 7. GA4 기준선 =====
ws = wb.create_sheet("GA4 매출 기준선")
title(ws, "GA4 일별 매출 — 광고 집행 전 기준선",
      "광고 효과를 판단하려면 '광고 켜기 전 매출'을 알아야 합니다. 이게 비교 기준입니다.")
head(ws, 4, ["날짜","요일","세션","거래수","매출","객단가","전환율","비고"], [12,7,10,10,14,13,10,34])
DOW = ["월","화","수","목","금","토","일"]
import datetime
r = 5
for d, ses, tx, rev in GA4:
    dt = datetime.date.fromisoformat(d)
    note = ""
    if d == "2026-09-21": note = "이상치 — 세션도 최저. 재조회에도 동일"
    if d == "2026-09-22": note = "광고 게재 시작일 / 집계 진행 중"
    ws.cell(row=r, column=1, value=d); ws.cell(row=r, column=2, value=DOW[dt.weekday()])
    ws.cell(row=r, column=3, value=ses); ws.cell(row=r, column=4, value=tx)
    ws.cell(row=r, column=5, value=rev).number_format = '#,##0"원"'
    ws.cell(row=r, column=6, value=f"=IF(D{r}=0,0,E{r}/D{r})").number_format = '#,##0"원"'
    ws.cell(row=r, column=7, value=f"=IF(C{r}=0,0,D{r}/C{r})").number_format = "0.00%"
    c = ws.cell(row=r, column=8, value=note)
    if note: c.font = WARN if "이상치" in note else SUB
    r += 1
ws.cell(row=r, column=1, value="평균(9/9~9/20)").font = Font(bold=True)
ws.cell(row=r, column=3, value="=ROUND(AVERAGE(C5:C16),0)").font = Font(bold=True)
ws.cell(row=r, column=4, value="=ROUND(AVERAGE(D5:D16),1)").font = Font(bold=True)
ws.cell(row=r, column=5, value="=ROUND(AVERAGE(E5:E16),0)").number_format = '#,##0"원"'
ws.cell(row=r, column=5).font = Font(bold=True)
ws.cell(row=r+2, column=1, value="해석 기준").font = Font(bold=True)
ws.cell(row=r+2, column=2, value="광고 시작 후 이 평균(거래 15.8건/일, 매출 약 1,485,000원/일)보다 올라가야 광고가 증분 매출을 만든 것입니다.")
ws.cell(row=r+3, column=2, value="구글애드 리포트의 '전환'은 광고 클릭에 귀속된 것만 셉니다. 전체 매출(위 표)과는 다른 숫자입니다 — 둘을 같이 봐야 합니다.")

# ===== 8. 운영 메모 =====
ws = wb.create_sheet("운영 메모")
title(ws, "어떻게 세팅했는가 · 확인할 것 · 수동 정리 항목")
ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 100
r = 4
def block(t, items):
    global r
    ws.cell(row=r, column=1, value=t).font = T_FONT; r += 1
    for it in items:
        ws.cell(row=r, column=1, value="·")
        ws.cell(row=r, column=2, value=it).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    r += 1

block("세팅 방법", [
 "Windsor.ai의 google_ads 커넥터(쓰기 권한)를 통해 Google Ads API로 생성했습니다. UI 마법사를 쓰지 않았습니다.",
 "당초 열려 있던 '실적 최대화(Performance Max)' 캠페인은 폐기했습니다 — 키워드 지정이 불가능해 「붓기·칼륨·젠제네틱스」 타겟을 만들 수 없기 때문입니다.",
 "캠페인 유형은 전부 검색(Search). 캠페인/광고그룹/광고/키워드/제외키워드/광고확장/위치/언어/입찰을 API로 설정했습니다.",
 "생성 시 전부 일시중지 상태로 만들고, 전환 추적과 결제 설정을 마친 뒤 게재를 시작했습니다.",
])
block("하루 뒤 확인할 것", [
 "검색어 보고서 — 실제 유입 검색어. 엉뚱한 검색이 있으면 제외 키워드 추가 (특히 BROAD 3건)",
 "광고 심의 상태 — 비승인 애셋 확인 (설인아 PICK / 1위 표현)",
 "평균 CPC 실측 — 설정한 상한(1,500 / 2,500 / 2,000원)이 적절한지",
 "위치(대한민국 2410)·언어(ko,en)·전환 기본목표 — 실적 행이 생기면 API 재조회로 교차 확인 가능",
 "GA4 9/21 거래 5건이 확정치인지",
])
block("구글애드 UI에서 수동 정리할 항목 (API로 삭제 불가)", [
 "잘못 생성된 구조화된 스니펫 애셋 423881840386 — 값이 '비타민B오플렉스'로 잘못 들어감. 브랜드방어 캠페인 → 애셋에서 삭제. 올바른 것(423782247365)은 이미 등록됨",
 "일시중지된 중복 광고 2개 — 199923244786~825567922000, 207170880944~825525918138. 최종 URL 슬러그 오타로 만들어졌다 교체됨. 삭제해도 무해",
 "기존 캠페인 3개 (PRE-WORKOUT / PROTEIN / BCAA) — 전부 일시중지. 과거 계정 이력이라 품질평가점수에는 유리. 그대로 둬도 됨",
])
block("아직 안 한 것", [
 "카페24 코드 직접입력의 깨진 인증 태그 수정 — name 속성 안에 토큰이 들어간 형태. name/content로 분리해야 함",
 "gtag 직접 설치 — GA4 가져오기로 대체했으므로 현재 불필요. 향상된 전환이 필요해지면 그때 추가",
 "카페24 상담실 번호 070-8800-1337 → 070-8872-1337 (상품 10개 페이지)",
])

out = "/tmp/젠제네틱스_구글광고_보고서.xlsx"
wb.save(out)
print("saved", out)
print("sheets:", wb.sheetnames)
