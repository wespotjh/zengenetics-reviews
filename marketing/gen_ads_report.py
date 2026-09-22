# -*- coding: utf-8 -*-
"""구글애드 운영 보고서 (8탭 xlsx → 구글 시트 변환 업로드).

일별 실적이 생기면 DAILY 에 (날짜, 캠페인, 노출, 클릭, 비용, 전환, 전환값) 을 넣고 다시 실행.
"""
import unicodedata as ud, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ACCOUNT, CURRENCY, START = "798-667-9268", "KRW", "2026-09-22"

CAMPAIGNS = [
    ("브랜드 방어", "젠제네틱스_브랜드방어_검색", "24281447473", "브랜드_전체", 10000, 1500, 17),
    ("붓기",       "젠제네틱스_붓기_검색",       "24270384426", "붓기_일반",   20000, 2500, 14),
    ("칼륨",       "젠제네틱스_칼륨_검색",       "24275789225", "칼륨_일반",   10000, 2000, 11),
]

KW = {
 "브랜드 방어": [("젠제네틱스","완전일치"),("젠제네틱스","구문일치"),("젠제네틱스 칼륨","구문일치"),
  ("젠제네틱스 붓기","구문일치"),("젠제네틱스 후기","구문일치"),("젠제네틱스 공식몰","구문일치"),
  ("젠제네틱스 마그네슘","구문일치"),("젠제네틱스 비타민B","구문일치"),("젠제네틱스 붓기파우더","구문일치"),
  ("zengenetics","완전일치"),("zengenetics","구문일치"),("zen genetics","구문일치"),
  ("zengenetic","구문일치"),("zengenetics korea","구문일치"),("zengenetics official","구문일치"),
  ("위스팟바이오랩","구문일치"),("wespot biolab","구문일치")],
 "붓기": [("붓기 영양제","구문일치"),("붓기 제거","구문일치"),("붓기 빼는 법","구문일치"),
  ("붓기파우더","구문일치"),("붓기 보조제","구문일치"),("얼굴 붓기","구문일치"),("다리 붓기","구문일치"),
  ("종아리 붓기","구문일치"),("아침 붓기","구문일치"),("붓기 차","구문일치"),("부종 영양제","구문일치"),
  ("수분 배출","구문일치"),("붓기 영양제","확장검색"),("붓기 칼륨","확장검색")],
 "칼륨": [("칼륨 영양제","구문일치"),("칼륨 보충제","구문일치"),("포타슘 영양제","구문일치"),
  ("구연산 칼륨","구문일치"),("칼륨 파우더","구문일치"),("칼륨 스틱","구문일치"),
  ("potassium 영양제","구문일치"),("칼륨 효능","구문일치"),("칼륨 부족","구문일치"),
  ("전해질 영양제","구문일치"),("칼륨 영양제","확장검색")],
}

NEG = [("무료","프리미엄만 노리는 검색"),("공짜","프리미엄만 노리는 검색"),
 ("부작용","구매 의도 낮음 + 심의 위험"),("후유증","구매 의도 낮음 + 심의 위험"),
 ("소송","부정 이슈"),("리콜","부정 이슈"),("환불","기존 고객 CS"),("해지","기존 고객 CS"),
 ("알바","구직"),("채용","구직"),("구인","구직"),("연봉","구직"),
 ("주가","투자 정보"),("상장","투자 정보"),
 ("도매","B2B"),("총판","B2B"),("대리점","B2B"),("제조사","B2B"),("OEM","B2B"),("ODM","B2B"),
 ("레시피","직접 만들려는 검색"),("만들기","직접 만들려는 검색"),("DIY","직접 만들려는 검색"),
 ("병원","의료 검색 — 우리는 식품"),("처방","의료 검색 — 우리는 식품"),("약국","의료 검색 — 우리는 식품"),
 ("의약품","★ 우리 제품은 의약품 아님"),("이뇨제","★ 의약품 검색, 심의 위험"),
 ("다이어트약","★ 의약품 검색, 심의 위험"),("토렌트","무관"),("중고","중고 거래")]

HL = {
"브랜드 방어": ["젠제네틱스 공식몰","젠제네틱스 붓기파우더","붓기파우더 공식 판매처","젠제네틱스 칼륨 525mg",
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
 "공식몰 구매하기","무료배송 당일출고","첫 구매 특가"]}
DS = {
"브랜드 방어": ["젠제네틱스 공식몰입니다. 칼륨·마그네슘·비타민B 정품만 판매합니다.",
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
 "구매 후기 333건 평균 4.77점. 공식몰에서 첫 구매 특가 확인하세요."]}

SL = [("붓기 칼륨","칼륨 525mg 분말스틱","하루 2포 간편 섭취","칼륨 상세 (11번)"),
 ("구매 후기","제품별 평점·후기 전체","매일 자동 갱신","review.zengenetics.co.kr"),
 ("첫 구매 특가","데이팩 6포 체험 구성","ID당 1회 한정","생애첫구매 (71번)"),
 ("붓기 부스터 세트","칼륨 2박스+비타민B","설인아 PICK","붓기부스터 SET (63번)")]
SL_K = SL[:3] + [("마그네슘","마그네슘 400mg 127%","건강기능식품","마그네슘 상세 (16번)")]
CO = {"브랜드 방어": ["무료배송","당일출고","올리브영 건강식품 1위","쿠팡 붓기 검색 1위"],
      "붓기": ["무료배송","당일출고","올리브영 건강식품 1위","쿠팡 붓기 검색 1위"],
      "칼륨": ["무료배송","당일출고","올리브영 건강식품 1위","후기 4.77점"]}

GA4 = [("2026-09-09",1007,19,774700),("2026-09-10",1313,13,585300),("2026-09-11",1178,12,505340),
 ("2026-09-12",1597,24,2094824),("2026-09-13",932,15,1202910),("2026-09-14",934,11,1282462),
 ("2026-09-15",1304,25,2984991),("2026-09-16",1193,14,1738612),("2026-09-17",1246,11,1278524),
 ("2026-09-18",1094,11,973840),("2026-09-19",964,16,2342940),("2026-09-20",1251,19,2062900),
 ("2026-09-21",753,5,182560),("2026-09-22",469,9,895220)]
BASE_N = 12   # 9/9~9/20 을 기준선 평균으로 사용

DAILY = []    # (날짜, 캠페인, 노출, 클릭, 비용, 전환, 전환값)

# ---------- 서식 ----------
NAVY = "1F3864"; LIGHT = "D9E2F3"; GREY = "F2F2F2"
def F(**k): return Font(**k)
HF = Font(color="FFFFFF", bold=True, size=10)
TITLE = Font(bold=True, size=14, color=NAVY)
SUBT  = Font(size=9, color="7F7F7F")
SEC   = Font(bold=True, size=11, color=NAVY)
BOLD  = Font(bold=True)
RED   = Font(bold=True, color="C00000")
GRN   = Font(bold=True, color="217346")
CEN   = Alignment(horizontal="center", vertical="center")
WRAP  = Alignment(vertical="top", wrap_text=True)
WON   = '#,##0"원"'
PCT   = '0.00%'

def glen(s): return sum(2 if ud.east_asian_width(c) in ("W","F") else 1 for c in str(s))

def setup(ws, title, sub, widths):
    ws["A1"] = title; ws["A1"].font = TITLE
    ws["A2"] = sub;   ws["A2"].font = SUBT
    ws.sheet_view.showGridLines = False
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 22

def header(ws, row, cols, freeze=True):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.fill = PatternFill("solid", fgColor=NAVY); cell.font = HF; cell.alignment = CEN
    ws.row_dimensions[row].height = 26
    if freeze: ws.freeze_panes = ws.cell(row=row+1, column=1)

def band(ws, row, text, span):
    """캠페인 구분용 연한 띠"""
    for i in range(1, span+1):
        c = ws.cell(row=row, column=i)
        c.fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=row, column=1, value=text).font = SEC

wb = Workbook()

# ══════════ 1. 대시보드 ══════════
ws = wb.active; ws.title = "대시보드"
setup(ws, "젠제네틱스 구글 검색광고",
      f"계정 {ACCOUNT}  ·  통화 {CURRENCY}  ·  게재 시작 {START}  ·  캠페인 유형 검색(Search)",
      [16, 30, 15, 10, 13, 13, 11, 14, 14])
r = 4
ws.cell(row=r, column=1, value="캠페인 현황").font = SEC; r += 1
header(ws, r, ["구분","캠페인 이름","광고그룹","상태","일 예산","CPC 상한","키워드","광고 제목","설명"], freeze=False)
r += 1
first = r
for short, name, cid, ag, bud, ceil, nkw in CAMPAIGNS:
    ws.cell(row=r, column=1, value=short).font = BOLD
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=ag)
    ws.cell(row=r, column=4, value="게재중").font = GRN
    ws.cell(row=r, column=4).alignment = CEN
    ws.cell(row=r, column=5, value=bud).number_format = WON
    ws.cell(row=r, column=6, value=ceil).number_format = WON
    ws.cell(row=r, column=7, value=nkw).alignment = CEN
    ws.cell(row=r, column=8, value="15개").alignment = CEN
    ws.cell(row=r, column=9, value="4개").alignment = CEN
    r += 1
ws.cell(row=r, column=1, value="합계").font = BOLD
ws.cell(row=r, column=5, value=f"=SUM(E{first}:E{r-1})").number_format = WON
ws.cell(row=r, column=5).font = BOLD
ws.cell(row=r, column=7, value=f"=SUM(G{first}:G{r-1})").font = BOLD
ws.cell(row=r, column=7).alignment = CEN
for i in range(1, 10):
    ws.cell(row=r, column=i).fill = PatternFill("solid", fgColor=GREY)

r += 3
ws.cell(row=r, column=1, value="광고 켜기 전 기준선  (GA4, 2026-09-09~09-20 평균)").font = SEC; r += 1
ws.cell(row=r, column=1, value="이 수치를 넘어야 광고가 실제로 매출을 만든 것입니다.").font = SUBT; r += 1
avg_t = sum(t for _,_,t,_ in GA4[:BASE_N]) / BASE_N
avg_r = sum(v for _,_,_,v in GA4[:BASE_N]) / BASE_N
avg_s = sum(s for _,s,_,_ in GA4[:BASE_N]) / BASE_N
header(ws, r, ["항목","값","","","","","","",""], freeze=False); r += 1
for k, v, fmt in [("일 세션", round(avg_s), '#,##0'),
                  ("일 거래수", round(avg_t, 1), '#,##0.0'),
                  ("일 매출", round(avg_r), WON),
                  ("객단가", round(avg_r/avg_t), WON),
                  ("전환율", avg_t/avg_s, PCT)]:
    ws.cell(row=r, column=1, value=k).font = BOLD
    c = ws.cell(row=r, column=2, value=v); c.number_format = fmt; r += 1

r += 2
ws.cell(row=r, column=1, value="전환 추적").font = SEC; r += 1
for k, v in [("방식","GA4 전환 가져오기 — 카페24에 gtag 코드를 심지 않았습니다"),
             ("전환 액션","젠제네틱스_속성 (web) purchase  ·  1개  ·  기본 목표"),
             ("전환 값","GA4가 보내는 실제 주문금액 → ROAS 계산 가능"),
             ("데이터 지연","24~48시간.  비용은 있는데 전환이 0인 날이 정상입니다"),
             ("gclid 유실","없음 — 랜딩 3개 URL × 데스크톱/모바일, 리다이렉트 0회 확인")]:
    ws.cell(row=r, column=1, value=k).font = BOLD
    ws.cell(row=r, column=2, value=v); r += 1

r += 2
ws.cell(row=r, column=1, value="예산").font = SEC; r += 1
for k, v in [("일 예산 합계","40,000원  →  월 약 120만원"),
             ("청구","청구 기준액 600,000원 도달 시 또는 매월 1일  ·  약 15일 주기"),
             ("결제 수단","국민카드 ••••1880  ·  후불"),
             ("지급인","주식회사 위스팟바이오랩")]:
    ws.cell(row=r, column=1, value=k).font = BOLD
    ws.cell(row=r, column=2, value=v); r += 1

# ══════════ 2. 일별 실적 ══════════
ws = wb.create_sheet("일별 실적")
setup(ws, "일별 실적",
      "게재 시작 2026-09-22.  CTR·평균CPC·CPA·ROAS·전환율은 수식으로 자동 계산됩니다.",
      [12, 14, 11, 10, 9, 12, 13, 9, 14, 12, 9, 10])
header(ws, 4, ["날짜","캠페인","노출","클릭","CTR","평균 CPC","비용","전환","전환값","CPA","ROAS","전환율"])
r = 5
if DAILY:
    for d, camp, imp, clk, cost, conv, cval in DAILY:
        ws.cell(row=r, column=1, value=d)
        ws.cell(row=r, column=2, value=camp)
        ws.cell(row=r, column=3, value=imp).number_format = '#,##0'
        ws.cell(row=r, column=4, value=clk).number_format = '#,##0'
        ws.cell(row=r, column=5, value=f"=IFERROR(D{r}/C{r},0)").number_format = PCT
        ws.cell(row=r, column=6, value=f"=IFERROR(G{r}/D{r},0)").number_format = WON
        ws.cell(row=r, column=7, value=cost).number_format = WON
        ws.cell(row=r, column=8, value=conv).number_format = '#,##0.0'
        ws.cell(row=r, column=9, value=cval).number_format = WON
        ws.cell(row=r, column=10, value=f"=IFERROR(G{r}/H{r},0)").number_format = WON
        ws.cell(row=r, column=11, value=f"=IFERROR(I{r}/G{r},0)").number_format = '0.00"배"'
        ws.cell(row=r, column=12, value=f"=IFERROR(H{r}/D{r},0)").number_format = PCT
        r += 1
else:
    ws.cell(row=5, column=1,
        value="아직 실적이 없습니다 — 오늘(2026-09-22) 게재를 시작했고, 광고 심의 통과 후 집계됩니다.").font = RED
    ws.cell(row=6, column=1,
        value="매일 제가 구글애드에서 조회해 이 표를 채웁니다.").font = SUBT
    ws.cell(row=8, column=1, value="지표 정의").font = SEC
    header(ws, 9, ["지표","계산식","보는 법","","","","","","","","",""], freeze=False)
    rows = [("CTR","클릭 ÷ 노출","검색광고는 5% 이상이면 양호. 브랜드 키워드는 15%도 나옵니다"),
            ("평균 CPC","비용 ÷ 클릭","설정한 상한(1,500/2,500/2,000원)보다 낮아야 정상"),
            ("CPA","비용 ÷ 전환","주문 1건을 따오는 데 든 광고비"),
            ("ROAS","전환값 ÷ 비용","1.0배 = 본전. 3배 이상이어야 남는 장사"),
            ("전환율","전환 ÷ 클릭","사이트 평균이 1.2% 수준이니 그 근처면 정상")]
    rr = 10
    for a, b, c in rows:
        ws.cell(row=rr, column=1, value=a).font = BOLD
        ws.cell(row=rr, column=2, value=b)
        ws.cell(row=rr, column=3, value=c); rr += 1

# ══════════ 3. 키워드 ══════════
ws = wb.create_sheet("키워드")
setup(ws, "등록 키워드 42개",
      "완전일치 = 이 검색어와 (거의) 똑같을 때만 노출  /  구문일치 = 이 어구를 포함한 검색에 노출  /  확장검색 = 관련 검색까지 폭넓게 노출",
      [18, 30, 14, 60])
header(ws, 4, ["캠페인","키워드","매치타입","비고"])
r = 5
for short, name, cid, ag, bud, ceil, nkw in CAMPAIGNS:
    band(ws, r, f"{short}  ({nkw}개)", 4); r += 1
    for kw, mt in KW[short]:
        ws.cell(row=r, column=2, value=kw)
        c = ws.cell(row=r, column=3, value=mt); c.alignment = CEN
        if mt == "확장검색":
            c.font = RED
            ws.cell(row=r, column=4, value="예산이 새기 쉬움 → 검색어 보고서 매일 확인").font = RED
        r += 1
    r += 1
ws.cell(row=r, column=1, value="메모").font = BOLD
ws.cell(row=r, column=2, value="문서 원안의 변형확장(+붓기 +영양제)은 구글이 2021년에 폐지했으므로 확장검색으로 변환해 등록했습니다.")

# ══════════ 4. 제외 키워드 ══════════
ws = wb.create_sheet("제외 키워드")
setup(ws, "제외 키워드 92개",
      "이 단어가 들어간 검색에는 광고가 나가지 않습니다. 예산이 새는 것을 막는 장치입니다.",
      [16, 13, 9, 9, 40])
header(ws, 4, ["제외 키워드","브랜드 방어","붓기","칼륨","제외 이유"])
r = 5
for kw, why in NEG:
    ws.cell(row=r, column=1, value=kw).font = BOLD
    b = "미적용" if kw == "무료" else "적용"
    c = ws.cell(row=r, column=2, value=b); c.alignment = CEN
    if b == "미적용": c.font = RED
    for col in (3, 4):
        ws.cell(row=r, column=col, value="적용").alignment = CEN
    c = ws.cell(row=r, column=5, value=why)
    if why.startswith("★"): c.font = RED
    r += 1
r += 1
ws.cell(row=r, column=1, value="예외").font = RED
ws.cell(row=r, column=2, value="브랜드 방어 캠페인에서만 '무료'를 빼뒀습니다 — 「젠제네틱스 무료배송」은 구매 직전 검색이라 막으면 손해입니다.")

# ══════════ 5. 광고 문안 ══════════
ws = wb.create_sheet("광고 문안")
setup(ws, "반응형 검색광고 문안  (캠페인별 광고 제목 15개 + 설명 4개)",
      "구글애드는 한글 1자를 2자로 계산합니다 → 광고 제목 한도 30(한글 15자), 설명 한도 90(한글 45자)",
      [18, 12, 6, 60, 9, 9, 9])
header(ws, 4, ["캠페인","유형","#","문안","자수","한도","여유"])
r = 5
for short, *_ in CAMPAIGNS:
    band(ws, r, short, 7); r += 1
    for i, h in enumerate(HL[short], 1):
        L = glen(h)
        ws.cell(row=r, column=2, value="광고 제목")
        ws.cell(row=r, column=3, value=i).alignment = CEN
        ws.cell(row=r, column=4, value=h)
        for col, v in ((5, L), (6, 30), (7, 30-L)):
            ws.cell(row=r, column=col, value=v).alignment = CEN
        r += 1
    for i, d in enumerate(DS[short], 1):
        L = glen(d)
        ws.cell(row=r, column=2, value="설명")
        ws.cell(row=r, column=3, value=i).alignment = CEN
        ws.cell(row=r, column=4, value=d)
        for col, v in ((5, L), (6, 90), (7, 90-L)):
            ws.cell(row=r, column=col, value=v).alignment = CEN
        r += 1
    r += 1
ws.cell(row=r, column=1, value="심의 주의").font = RED
ws.cell(row=r, column=4, value="「설인아 PICK 젠제네틱스」= 유명인 이름 / 「올리브영·쿠팡 1위」= 최상급 표현.")
ws.cell(row=r+1, column=4, value="반응형 검색광고는 문안 하나씩 심의되므로, 한 개가 비승인돼도 광고 전체는 계속 게재됩니다.")

# ══════════ 6. 광고 확장 ══════════
ws = wb.create_sheet("광고 확장")
setup(ws, "광고 확장  (사이트링크 12 · 콜아웃 12 · 구조화된 스니펫 3 · 전화번호 3)",
      "검색 결과에서 광고 아래에 같이 붙는 부가 정보입니다. 광고 면적이 커져 클릭률이 올라갑니다.",
      [18, 18, 22, 24, 24, 26])
header(ws, 4, ["캠페인","유형","표시 텍스트","설명 1","설명 2 / 값","연결 페이지"])
r = 5
for short, *_ in CAMPAIGNS:
    band(ws, r, short, 6); r += 1
    for t, d1, d2, u in (SL_K if short == "칼륨" else SL):
        ws.cell(row=r, column=2, value="사이트링크")
        ws.cell(row=r, column=3, value=t); ws.cell(row=r, column=4, value=d1)
        ws.cell(row=r, column=5, value=d2); ws.cell(row=r, column=6, value=u); r += 1
    for co in CO[short]:
        ws.cell(row=r, column=2, value="콜아웃")
        ws.cell(row=r, column=3, value=co); r += 1
    ws.cell(row=r, column=2, value="구조화된 스니펫")
    ws.cell(row=r, column=3, value="Types")
    ws.cell(row=r, column=5, value="칼륨 / 마그네슘 / 비타민B컴플렉스 / 데이팩 / 세트"); r += 1
    ws.cell(row=r, column=2, value="전화번호")
    ws.cell(row=r, column=3, value="070-8872-1337")
    ws.cell(row=r, column=4, value="국가 KR"); r += 2

# ══════════ 7. GA4 기준선 ══════════
ws = wb.create_sheet("GA4 매출 기준선")
setup(ws, "GA4 일별 매출 — 광고 집행 전 기준선",
      "광고 효과는 '광고 켜기 전 매출'과 비교해야 판단됩니다. 이게 그 비교 기준입니다.",
      [13, 8, 11, 11, 15, 14, 10, 34])
header(ws, 4, ["날짜","요일","세션","거래수","매출","객단가","전환율","비고"])
DOW = ["월","화","수","목","금","토","일"]
r = 5; first = r
for d, s, t, v in GA4:
    dt = datetime.date.fromisoformat(d)
    ws.cell(row=r, column=1, value=d)
    ws.cell(row=r, column=2, value=DOW[dt.weekday()]).alignment = CEN
    ws.cell(row=r, column=3, value=s).number_format = '#,##0'
    ws.cell(row=r, column=4, value=t).number_format = '#,##0'
    ws.cell(row=r, column=5, value=v).number_format = WON
    ws.cell(row=r, column=6, value=f"=IFERROR(E{r}/D{r},0)").number_format = WON
    ws.cell(row=r, column=7, value=f"=IFERROR(D{r}/C{r},0)").number_format = PCT
    if d == "2026-09-21":
        ws.cell(row=r, column=8, value="이상치 — 세션도 최저. 재조회해도 동일").font = RED
    if d == "2026-09-22":
        ws.cell(row=r, column=8, value="광고 게재 시작일 / 집계 진행 중").font = SUBT
    r += 1
last_base = first + BASE_N - 1
ws.cell(row=r, column=1, value="기준선 평균").font = BOLD
ws.cell(row=r, column=2, value="9/9~9/20").font = SUBT
ws.cell(row=r, column=3, value=f"=ROUND(AVERAGE(C{first}:C{last_base}),0)").number_format = '#,##0'
ws.cell(row=r, column=4, value=f"=ROUND(AVERAGE(D{first}:D{last_base}),1)").number_format = '#,##0.0'
ws.cell(row=r, column=5, value=f"=ROUND(AVERAGE(E{first}:E{last_base}),0)").number_format = WON
ws.cell(row=r, column=6, value=f"=IFERROR(E{r}/D{r},0)").number_format = WON
ws.cell(row=r, column=7, value=f"=IFERROR(D{r}/C{r},0)").number_format = PCT
for i in range(1, 9):
    ws.cell(row=r, column=i).fill = PatternFill("solid", fgColor=GREY)
    if i in (3,4,5): ws.cell(row=r, column=i).font = BOLD
r += 2
ws.cell(row=r, column=1, value="주의").font = BOLD
ws.cell(row=r, column=2, value="구글애드의 '전환'은 광고 클릭에 귀속된 주문만 셉니다. 위 전체 매출과는 다른 숫자이니 둘을 같이 봐야 합니다.")

# ══════════ 8. 운영 메모 ══════════
ws = wb.create_sheet("운영 메모")
setup(ws, "어떻게 세팅했는가 · 확인할 것 · 남은 일", "", [4, 110])
r = 4
def block(t, items, color=None):
    global r
    ws.cell(row=r, column=1, value="").fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=2, value=t).font = SEC
    r += 1
    for it in items:
        ws.cell(row=r, column=1, value="·").alignment = CEN
        c = ws.cell(row=r, column=2, value=it); c.alignment = WRAP
        if color: c.font = color
        ws.row_dimensions[r].height = 15
        r += 1
    r += 1

block("세팅 방법", [
 "Windsor.ai의 google_ads 커넥터(쓰기 권한)로 Google Ads API를 직접 호출해 만들었습니다. UI 마법사를 쓰지 않았습니다.",
 "처음 열려 있던 '실적 최대화(Performance Max)' 캠페인은 폐기했습니다 — 키워드를 지정할 수 없어 붓기·칼륨·젠제네틱스 타겟이 불가능합니다.",
 "캠페인 3개 / 광고그룹 3개 / 광고 3개 / 키워드 42개 / 제외 키워드 92개 / 광고 확장 30개 / 위치 / 언어 / 입찰을 모두 API로 설정했습니다.",
 "전부 일시중지 상태로 만든 뒤, 전환 추적과 결제 설정을 마치고 게재를 시작했습니다.",
 "등록한 키워드 42개는 등록 후 다시 읽어 한글이 깨지지 않았음을 확인했습니다.",
])
block("하루 뒤 확인할 것", [
 "검색어 보고서 — 실제 어떤 검색어로 들어왔는지. 엉뚱한 검색이 있으면 제외 키워드 추가 (특히 확장검색 3건)",
 "광고 심의 상태 — 비승인된 문안이 있는지 (설인아 PICK / 1위 표현)",
 "평균 CPC 실측 — 설정한 상한 1,500 / 2,500 / 2,000원이 적절한지",
 "위치(대한민국) · 언어(한국어+영어) · 전환 기본목표 — 실적 행이 생기면 API로 재조회해 교차 확인",
 "GA4 9월 21일 거래 5건이 확정 수치인지",
])
block("구글애드 UI에서 직접 지워야 하는 것 (API로 삭제 불가)", [
 "구조화된 스니펫 애셋 423881840386 — 값이 '비타민B오플렉스'로 잘못 만들어졌습니다. 브랜드 방어 캠페인 → 애셋에서 삭제하세요. 올바른 것(423782247365)은 이미 등록돼 있습니다.",
 "일시중지된 중복 광고 2개 (199923244786~825567922000 / 207170880944~825525918138) — 최종 URL 슬러그 오타로 만들었다 교체한 것입니다. 지워도 무해합니다.",
 "기존 캠페인 PRE-WORKOUT / PROTEIN / BCAA — 전부 일시중지 상태입니다. 과거 계정 이력이라 품질평가점수에는 오히려 유리하니 그대로 두셔도 됩니다.",
], RED)
block("아직 안 한 일", [
 "카페24 코드 직접입력의 깨진 인증 태그 수정 — name 속성 안에 토큰이 들어간 형태입니다. name과 content로 분리해야 합니다.",
 "gtag 직접 설치 — GA4 가져오기로 대체했으므로 지금은 불필요합니다. 향상된 전환이 필요해지면 그때 추가합니다.",
 "카페24 소비자 상담실 번호 070-8800-1337 → 070-8872-1337 (상품 10개 페이지)",
])

out = "/tmp/zengenetics-google-ads-report.xlsx"
wb.save(out)
print("saved", out)
print("tabs:", " | ".join(wb.sheetnames))
