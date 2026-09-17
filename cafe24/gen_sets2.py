# -*- coding: utf-8 -*-
"""세트·데이팩·이벤트 7종 전체 교체 코드 생성 (2단계: 텍스트 블록 + 파일 출력)."""
import json, re, html

S = '/tmp/claude-0/-home-user-starbucks/9355b6cf-24b5-5db0-83cb-cbab6470358a/scratchpad/'
D = json.load(open(S+'sha.json', encoding='utf-8'))
PAGES, SHA = D['pages'], D['sha']
ALT = json.load(open(S+'altsha.json', encoding='utf-8'))
TAGS = json.load(open(S+'settags.json', encoding='utf-8'))

def esc(s): return html.escape(str(s), quote=True).replace('&#x27;', "'")

# ══ 조합 설명 — 검토 후 이 두 상수만 고치면 해당 페이지 전체에 반영된다 ══
COMBO_SWELL = ("칼륨은 짠 식습관으로 과해진 나트륨 배출을 돕고, 비타민B컴플렉스는 에너지 생성과 "
               "대사에 필요한 영양소로 수분 순환을 도와 더 빠른 붓기 케어를 돕습니다.")
COMBO_PERF  = ("마그네슘은 신경과 근육 기능 유지에 필요하고, 비타민B컴플렉스는 에너지 생성과 대사에 "
               "필요합니다. 운동과 업무로 소모되는 두 영양소를 함께 채우는 조합입니다.")
COMBO_KMB   = ("칼륨으로 나트륨 배출을, 마그네슘으로 신경과 근육 기능 유지를, 비타민B컴플렉스로 "
               "에너지 생성과 대사를 함께 챙기는 하루 루틴 구성입니다.")

FONT = ("font:15px/1.8 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo',"
        "'Malgun Gothic',sans-serif;color:#15161A")
THS = "text-align:left;vertical-align:top;padding:9px 12px 9px 0;border-top:1px solid #E9E8E4;font-weight:600"
TDS = "padding:9px 0;border-top:1px solid #E9E8E4"
GRAY = 'style="color:#93959D;font-size:12.5px;margin:0 0 30px"'

def imgs(no):
    out=[]
    for t,u in zip(TAGS[no], PAGES[no]):
        tag = t['tag'].replace('ec-data-src=','src=')
        assert ' src=' in tag
        a = ALT[SHA[u]].replace('"','“')
        out.append(tag.replace('<img ', f'<img alt="{a}" ', 1))
    return ''.join(out)

def qa(q,a):
    return (f'  <div style="border-top:1px solid #E9E8E4;padding:16px 0">\n'
            f'    <h3 style="font-size:15.5px;margin:0 0 6px">{esc(q)}</h3>\n'
            f'    <p style="margin:0;color:#3F4149">{esc(a)}</p>\n  </div>\n\n')

def rows(pairs):
    return ''.join(f'      <tr><th style="{"width:150px;" if i==0 else ""}{THS}">{esc(k)}</th>'
                   f'<td style="{TDS}">{esc(v)}</td></tr>\n' for i,(k,v) in enumerate(pairs))

def ld(qas):
    return ('\n<script type="application/ld+json">\n' + json.dumps(
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,
             "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qas]},
        ensure_ascii=False) + '\n</script>\n')

LINK = ('  <p style="margin:28px 0 0;font-size:14.5px">\n'
        '    <a href="https://review.zengenetics.co.kr/">젠제네틱스 구매 후기 전체 보기</a>\n'
        '  </p>\n</div>\n')

def block(title, sub, intro, qas, spec, note):
    h  = f'<div style="max-width:860px;margin:48px auto 0;padding:0 20px;{FONT}">\n\n'
    h += f'  <h2 style="font-size:19px;margin:0 0 6px">{esc(title)}</h2>\n'
    h += f'  <p style="color:#5F626C;font-size:14px;margin:0 0 12px">{esc(sub)}</p>\n'
    h += f'  <p style="margin:0 0 8px;color:#3F4149">{esc(intro)}</p>\n'
    h += f'  <p {GRAY}>{esc(note)}</p>\n\n'
    h += '  <h2 style="font-size:19px;margin:0 0 18px">자주 묻는 질문</h2>\n\n'
    for q,a in qas: h += qa(q,a)
    h += '  <h2 style="font-size:19px;margin:40px 0 14px">구성 및 제품정보</h2>\n'
    h += '  <table style="width:100%;border-collapse:collapse;font-size:14.5px">\n    <tbody>\n'
    h += rows(spec)
    h += '    </tbody>\n  </table>\n'
    return h + LINK + ld(qas)

MAKER='콜마비앤에이치(주) 세종 3공장'; SELLER='(주)위스팟'; TEL='070-8800-1337'
K_20  = ('칼륨','젠제네틱스 포타슘 칼륨525mg 다이렉트 · 2.5g×20포(50g) · 당류가공품 · '
         '품목보고번호 20240365166-114 · 1일 2회 1회 1포 · 1포당 칼륨 262.5mg')
K_6   = ('칼륨','젠제네틱스 포타슘 칼륨525mg 다이렉트 · 2.5g×6포(15g) · 당류가공품 · '
         '품목보고번호 20240365166-114 · 1일 2회 1회 1포 · 1포당 칼륨 262.5mg, 열량 8kcal, 당류 1.3g')
M_20  = ('마그네슘','젠제네틱스 마그네슘 400mg 다이렉트 · 2g×20포(40g) · 건강기능식품 · '
         '1일 1회 1포 · 1포당 마그네슘 400mg(127%), 열량 4kcal')
M_6   = ('마그네슘','젠제네틱스 마그네슘 400mg 다이렉트 · 2g×6포(12g) · 건강기능식품 · '
         '1일 1회 1포 · 1포당 마그네슘 400mg(127%), 열량 4kcal')
B_20  = ('비타민B컴플렉스','젠제네틱스 비타민B 컴플렉스 다이렉트 · 2g×20포(40g) · 건강기능식품 · '
         '1일 1회 1포 · 1포당 B1 3.6mg·B2 4.2mg·B6 4.5mg·B12 7.2µg(각 300%), 열량 8kcal')
B_6   = ('비타민B컴플렉스','젠제네틱스 비타민B 컴플렉스 다이렉트 · 2g×6포(12g) · 건강기능식품 · '
         '1일 1회 1포 · 1포당 B1 3.6mg·B2 4.2mg·B6 4.5mg·B12 7.2µg(각 300%), 열량 8kcal')
COMMON=[('제조원',MAKER),('판매원',SELLER),('소비자 상담실',TEL)]

FN_HGF = ('마그네슘 : 에너지 이용에 필요, 신경과 근육 기능 유지에 필요 / '
          '비타민B1 : 탄수화물과 에너지 대사에 필요 / 비타민B2 : 체내 에너지 생성에 필요 / '
          '비타민B6 : 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 / '
          '비타민B12 : 정상적인 엽산 대사에 필요')
NOTE_MIX = ('마그네슘·비타민B컴플렉스는 건강기능식품이며 기능성 내용은 ' + FN_HGF +
            '. 칼륨 제품의 식품유형은 당류가공품이며 건강기능식품이 아닙니다. '
            '본 제품은 질병의 예방 및 치료를 위한 의약품이 아닙니다.')
NOTE_K   = ('본 제품의 식품유형은 당류가공품이며 건강기능식품이 아닙니다. '
            '본 제품은 질병의 예방 및 치료를 위한 의약품이 아닙니다.')
NOTE_HGF = ('본 제품은 건강기능식품이며 질병의 예방 및 치료를 위한 의약품이 아닙니다. '
            '이상사례 신고는 1577-2488.')

Q_DP = "데이팩 6포는 며칠분인가요?"
SPECS={
 '63':[K_20,K_20,B_20]+COMMON, '64':[M_20,B_20]+COMMON, '98':[K_20,M_20,B_20]+COMMON,
 '60':[K_6]+COMMON, '61':[M_6]+COMMON, '62':[B_6]+COMMON,
 '71':[K_6,M_6,B_6]+COMMON,
}

CFG = {
 '63': dict(title='붓기 부스터 세트 — 칼륨 2박스 + 비타민B컴플렉스 1박스',
   sub='설인아 PICK 붓기 부스터 젠제네틱스 칼륨(2box) & 비타민B컴플렉스(1box) SET',
   intro=COMBO_SWELL + ' 그래서 붓기 부스터 세트는 칼륨 2박스와 비타민B컴플렉스 1박스로 구성했습니다.',
   note=NOTE_MIX,
   qas=[("붓기엔 칼륨만 먹으면 되나요? 비타민B를 왜 같이 먹나요?", COMBO_SWELL +
         " 그래서 칼륨 2박스에 비타민B컴플렉스 1박스를 함께 구성했습니다."),
        ("두 제품을 같이 먹어도 되나요?",
         "네. 칼륨은 1일 2회 1회 1포, 비타민B컴플렉스는 1일 1회 1포로 섭취 시점이 겹쳐도 무방합니다. "
         "둘 다 물 없이 먹는 분말 스틱입니다."),
        ("칼륨이 2박스인 이유가 있나요?",
         "칼륨은 1일 2회 1포씩 섭취해 20포 1박스가 10일분이고, 비타민B컴플렉스는 1일 1회 1포로 "
         "20포가 20일분입니다. 칼륨 2박스와 비타민B 1박스를 맞추면 같은 기간으로 떨어집니다."),
        ("언제 먹는 게 좋나요?",
         "칼륨은 아침 얼굴이 붓는 타입은 자기 전 1포와 기상 직후 1포, 저녁 종아리가 붓는 타입은 "
         "출근 전 1포와 오후 3시 1포를 권합니다. 비타민B컴플렉스는 하루를 시작하는 아침 루틴으로 "
         "설계되었습니다."),
        ("각각 뭐가 들었나요?",
         "칼륨은 1포당 구연산 칼륨 262.5mg(독일 Jungbunzlauer사 원료), 비타민B컴플렉스는 1포당 "
         "비타민B1 3.6mg·B2 4.2mg·B6 4.5mg·B12 7.2µg으로 각각 1일 영양성분 기준치의 300%입니다"
         "(DSM사 독일·스위스산 원료).")]),
 '64': dict(title='퍼포먼스 부스터 세트 — 마그네슘 1박스 + 비타민B컴플렉스 1박스',
   sub='퍼포먼스 부스터 젠제네틱스 마그네슘(1box) & 비타민B컴플렉스(1box) SET',
   intro=COMBO_PERF, note=NOTE_HGF,
   qas=[("마그네슘과 비타민B를 왜 같이 먹나요?", COMBO_PERF),
        ("두 제품 다 건강기능식품인가요?",
         "네. 둘 다 식품유형이 건강기능식품이며, 기능성 내용은 마그네슘은 에너지 이용에 필요·"
         "신경과 근육 기능 유지에 필요, 비타민B군은 에너지 대사와 생성에 필요입니다."),
        ("언제 먹는 게 좋나요?",
         "마그네슘은 하루를 마무리하는 저녁 루틴, 비타민B컴플렉스는 하루를 시작하는 아침 루틴으로 "
         "설계되었습니다. 각각 1일 1회 1포입니다."),
        ("운동하는 날만 먹어도 되나요?",
         "마그네슘은 매일 소모되고 배출되는 미네랄이라 운동 여부와 관계없이 하루 한 포를 권하며, "
         "운동한 날은 운동 후에서 취침 전에 섭취하시는 것이 좋습니다."),
        ("각각 뭐가 들었나요?",
         "마그네슘은 1포당 400mg으로 1일 영양성분 기준치의 127%(미국 aic사 순도 97.4% "
         "산화마그네슘), 비타민B컴플렉스는 1포당 B1 3.6mg·B2 4.2mg·B6 4.5mg·B12 7.2µg으로 각 "
         "300%입니다(DSM사 독일·스위스산 원료).")]),
 '98': dict(title='칼마비 건강루틴 세트 — 칼륨 + 마그네슘 + 비타민B컴플렉스',
   sub='칼마비 건강루틴 젠제네틱스 칼륨 + 마그네슘 + 비타민B컴플렉스 SET',
   intro=COMBO_KMB, note=NOTE_MIX,
   qas=[("세 가지를 같이 먹는 이유가 뭔가요?", COMBO_KMB),
        ("세 개를 하루에 다 먹어도 되나요?",
         "네. 칼륨은 1일 2회 1회 1포, 마그네슘과 비타민B컴플렉스는 각각 1일 1회 1포입니다. "
         "모두 물 없이 먹는 분말 스틱입니다."),
        ("어떻게 나눠 먹으면 되나요?",
         "비타민B컴플렉스는 아침, 마그네슘은 저녁 루틴으로 설계되었습니다. 칼륨은 아침 얼굴이 붓는 "
         "타입은 자기 전과 기상 직후, 저녁 종아리가 붓는 타입은 출근 전과 오후 3시를 권합니다."),
        ("칼륨도 건강기능식품인가요?",
         "아닙니다. 마그네슘과 비타민B컴플렉스는 건강기능식품이고, 칼륨의 식품유형은 당류가공품입니다."),
        ("주의해야 할 사람이 있나요?",
         "마그네슘은 신장 질환이 있거나 신장 기능이 저하된 분은 전문가와 상담 후 섭취를 권하며, "
         "임신·수유 중에는 전문의와 상담 후 섭취하시길 권장드립니다.")]),
 '60': dict(title='칼륨 데이팩 (6ea) — 6일 체험 구성',
   sub='젠제네틱스 포타슘 칼륨 데이팩 2.5g×6포',
   intro='20포 정품과 같은 제품을 6포 구성으로 담았습니다. 처음 드셔보시는 분께 권합니다.',
   note=NOTE_K,
   qas=[(Q_DP, "칼륨은 1일 2회 1회 1포 섭취라 6포는 3일분입니다. 20포 정품은 10일분입니다."),
        ("20포 제품과 내용이 다른가요?",
         "같습니다. 1포당 칼륨 262.5mg, 원재료와 제조원 모두 동일하며 포수만 다릅니다."),
        ("어떻게 먹나요?",
         "1일 2회 1회 1포입니다. 아침 얼굴이 붓는 타입은 자기 전 1포와 기상 직후 1포, 저녁 종아리가 "
         "붓는 타입은 출근 전 1포와 오후 3시 1포를 권합니다. 물 없이 먹는 분말 스틱입니다.")]),
 '61': dict(title='마그네슘 데이팩 (6ea) — 6일 체험 구성',
   sub='젠제네틱스 마그네슘 데이팩 2g×6포',
   intro='20포 정품과 같은 제품을 6포 구성으로 담았습니다. 처음 드셔보시는 분께 권합니다.',
   note=NOTE_HGF,
   qas=[(Q_DP, "마그네슘은 1일 1회 1포 섭취라 6포는 6일분입니다. 20포 정품은 20일분입니다."),
        ("20포 제품과 내용이 다른가요?",
         "같습니다. 1포당 마그네슘 400mg(1일 영양성분 기준치의 127%), 원재료와 제조원 모두 "
         "동일하며 포수만 다릅니다."),
        ("주의해야 할 사람이 있나요?",
         "신장 질환이 있거나 신장 기능이 저하된 분은 전문가와 상담 후 섭취를 권장드립니다.")]),
 '62': dict(title='비타민B컴플렉스 데이팩 (6ea) — 6일 체험 구성',
   sub='젠제네틱스 비타민B컴플렉스 데이팩 2g×6포',
   intro='20포 정품과 같은 제품을 6포 구성으로 담았습니다. 처음 드셔보시는 분께 권합니다.',
   note=NOTE_HGF,
   qas=[(Q_DP, "비타민B컴플렉스는 1일 1회 1포 섭취라 6포는 6일분입니다. 20포 정품은 20일분입니다."),
        ("20포 제품과 내용이 다른가요?",
         "같습니다. 1포당 비타민B1 3.6mg·B2 4.2mg·B6 4.5mg·B12 7.2µg(각 1일 영양성분 기준치의 "
         "300%), 원재료와 제조원 모두 동일하며 포수만 다릅니다."),
        ("섭취 후 소변이 노랗게 변했는데 괜찮은건가요?",
         "비타민B2의 영향으로 소변의 색이 변할 수 있습니다. 수용성 비타민이 배출되며 나타나는 "
         "자연스러운 현상입니다.")]),
 '71': dict(title='생애 첫 구매 EVENT — 칼륨 · 마그네슘 · 비타민B컴플렉스 데이팩',
   sub='젠제네틱스 체험 EVENT, 데이팩 6포 구성에서 선택',
   intro='칼륨·마그네슘·비타민B컴플렉스 데이팩 중에서 골라 처음 체험해보실 수 있습니다. ' + COMBO_KMB,
   note=NOTE_MIX + ' ID당 한번만 구매 가능하며 재고 소진 시 종료될 수 있습니다.',
   qas=[("어떤 걸 고르면 되나요?",
         "붓기가 고민이면 칼륨, 긴장과 컨디션이 고민이면 마그네슘, 활력이 고민이면 비타민B컴플렉스를 "
         "권합니다. 붓기는 칼륨과 비타민B컴플렉스를 함께 쓰는 조합도 있습니다."),
        ("붓기엔 뭘 고르는 게 좋나요?", COMBO_SWELL),
        (Q_DP, "칼륨은 1일 2회 1포씩이라 6포가 3일분, 마그네슘과 비타민B컴플렉스는 1일 1회 1포라 "
               "6포가 각각 6일분입니다."),
        ("정품과 내용이 다른가요?",
         "같습니다. 1포당 함량과 원재료, 제조원이 모두 동일하며 포수만 다릅니다."),
        ("구매 조건이 있나요?",
         "ID당 한번만 구매 가능하며 재고 소진 시 종료될 수 있고, 배송비 무료쿠폰은 사용할 수 없습니다.")]),
}

NAMES={'63':'set-swell','64':'set-performance','98':'set-kmb',
       '60':'daypack-potassium','61':'daypack-magnesium','62':'daypack-vitaminb',
       '71':'first-buy'}
for no,c in CFG.items():
    body = imgs(no) + '\n\n' + block(c['title'],c['sub'],c['intro'],c['qas'],SPECS[no],c['note'])
    p=f"cafe24/{NAMES[no]}_FULL.txt"
    open(p,'w',encoding='utf-8').write(body)
    print(f"{p:<42} {len(body.encode()):>6} bytes | img {body.count('<img ')} | Q {len(c['qas'])}")
