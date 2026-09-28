# -*- coding: utf-8 -*-
"""젠제네틱스 — 파비콘 + 구글 검색광고 이미지 애셋 생성.

원본 렌더는 별도 저장소에 있다: /home/user/wespotjh/zengenetics/assets/
  render/potassium_box20_turn/frame_0001.png   900x900 RGBA (박스 정면)
  render/potassium_box20_open/frame_0001.png   900x900 RGBA (박스 사선)
  stick-pot-gen.png                            261x1200 RGBA (세로 스틱)

브랜드 네이비 #092D74 는 기존 파비콘에서 추출했다. 별도 로고 파일은 없다.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
SRC = "/home/user/wespotjh/zengenetics/assets/render/"
NAVY  = (9, 45, 116)      # 현재 파비콘에서 추출한 브랜드 네이비
PAPER = (251, 250, 248)   # 브랜드 페이퍼 톤

# ── 1. 파비콘 ─────────────────────────────────────────────
def zmark(size, ss=8):
    """네이비 원 + 흰 Z. ss배 확대해 그린 뒤 축소(안티에일리어싱)."""
    S = size * ss
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, S - 1, S - 1], fill=NAVY + (255,))

    # Z 폴리곤 — 원 안쪽 정사각 영역에 배치
    m = S * 0.255                     # 좌우 여백
    x0, x1 = m, S - m
    y0, y1 = S * 0.285, S * 0.715
    t = (y1 - y0) * 0.255             # 가로 바 두께
    s = (x1 - x0) * 0.30              # 대각선 수평 두께

    pts = [(x0, y0), (x1, y0), (x1, y0 + t), (x0 + s, y1 - t),
           (x1, y1 - t), (x1, y1), (x0, y1), (x0, y1 - t),
           (x1 - s, y0 + t), (x0, y0 + t)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)

sizes = [48, 96, 144, 192, 256]
icons = {n: zmark(n) for n in sizes}
icons[256].save(os.path.join(OUT, "favicon-256.png"))
icons[192].save(os.path.join(OUT, "favicon-192.png"))
icons[144].save(os.path.join(OUT, "favicon-144.png"))
# 멀티사이즈 ICO (48/96/144) — 구글은 48의 배수를 요구
icons[144].save(os.path.join(OUT, "favicon.ico"),
                sizes=[(48, 48), (96, 96), (144, 144)])

# ── 2. 구글 광고 이미지 애셋 ───────────────────────────────
def compose(src, W, H, fill=0.74, name="out.png"):
    """제품 렌더를 브랜드 배경 위에 그림자와 함께 배치."""
    p = Image.open(SRC + src).convert("RGBA")
    p = p.crop(p.getbbox())                       # 투명 여백 제거

    box_w, box_h = W * fill, H * fill
    r = min(box_w / p.width, box_h / p.height)
    p = p.resize((max(1, round(p.width * r)), max(1, round(p.height * r))), Image.LANCZOS)

    bg = Image.new("RGBA", (W, H), PAPER + (255,))
    x = (W - p.width) // 2
    y = (H - p.height) // 2

    # 부드러운 접지 그림자
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [x + p.width * 0.10, y + p.height * 0.90,
         x + p.width * 0.90, y + p.height * 1.03],
        fill=(20, 22, 28, 52))
    sh = sh.filter(ImageFilter.GaussianBlur(max(6, W // 55)))
    bg.alpha_composite(sh)
    bg.alpha_composite(p, (x, y))

    out = os.path.join(OUT, name)
    bg.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    return out, os.path.getsize(out)

specs = [
    ("potassium_box20_turn/frame_0001.png", 1200, 1200, 0.70, "ads_1x1_1200.jpg",  "정사각 1:1 (필수)"),
    ("potassium_box20_open/frame_0001.png", 1200,  628, 0.80, "ads_191x1_1200.jpg","가로 1.91:1 (권장)"),
    ("potassium_stick/frame_0001.png",       960, 1200, 0.72, "ads_4x5_960.jpg",   "세로 4:5 (선택)"),
]

print("=== 파비콘 ===")
for n in sizes:
    f = os.path.join(OUT, "favicon-%d.png" % n)
    if os.path.exists(f):
        print("  favicon-%d.png  %d bytes" % (n, os.path.getsize(f)))
print("  favicon.ico (48/96/144 멀티)  %d bytes" % os.path.getsize(os.path.join(OUT, "favicon.ico")))

print("\n=== 구글 광고 이미지 애셋 ===")
LIMIT = 5120 * 1024
for src, w, h, fill, name, label in specs:
    path, sz = compose(src, w, h, fill, name)
    im = Image.open(path)
    ok = "OK" if (sz <= LIMIT) else "초과"
    print("  %-22s %4dx%-5d %6.0f KB  %s  %s" % (name, im.width, im.height, sz / 1024, ok, label))
print("\n  구글 한도: 1:1 최소 300x300(권장 1200x1200) / 1.91:1 최소 600x314(권장 1200x628)")
print("             4:5 최소 480x600(권장 960x1200) / 파일 5MB 이하 / JPG·PNG")
