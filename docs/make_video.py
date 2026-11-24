# ============================================================
#  BUILD THE DEMO VIDEO
#  Run from the project folder:  python docs/make_video.py
#  Needs: pillow, numpy and opencv-python (already used by tests).
#  Output: docs/demo.mp4  (1280x720, 22 seconds, silent)
# ============================================================

import math
import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FPS = 30
DURATION = 22.0
FRAMES = int(FPS * DURATION)

HERE = os.path.dirname(os.path.abspath(__file__))
SHOT_PATH = os.path.join(HERE, "screenshot.png")
OUT_PATH = os.path.join(HERE, "demo.mp4")

# ---- colours (same family as the app) ----
BG = (11, 18, 32)
TEXT = (232, 238, 247)
MUTED = (142, 163, 192)
BLUE = (59, 130, 246)
SKY = (14, 165, 233)
GREEN = (34, 197, 94)
PURPLE = (139, 92, 246)
ORANGE = (245, 158, 11)
RED = (239, 68, 68)
TEAL = (20, 184, 166)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

_font_cache = {}


def font(size, kind="bold"):
    key = (size, kind)
    if key not in _font_cache:
        path = {"bold": FONT_BOLD, "regular": FONT_REG, "mono": FONT_MONO}[kind]
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = max(0.0, min(1.0, x))
    return 3 * x * x - 2 * x * x * x


def lerp(a, b, x):
    return a + (b - a) * x


def scene_alpha(t, start, end, fade=0.35):
    if t < start or t > end:
        return 0.0
    return min(1.0, (t - start) / fade, (end - t) / fade)


def make_background():
    """Dark gradient with soft coloured glows."""
    base = Image.new("RGB", (W, H), BG)
    px = base.load()
    top, bottom = np.array(BG), np.array((15, 26, 46))
    for y in range(H):
        k = y / (H - 1)
        colour = tuple(int(lerp(top[i], bottom[i], k)) for i in range(3))
        for x in range(W):
            px[x, y] = colour

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse([-260, -240, 460, 420], fill=BLUE + (55,))
    d.ellipse([900, -260, 1500, 300], fill=PURPLE + (45,))
    d.ellipse([820, 470, 1460, 1040], fill=GREEN + (30,))
    d.ellipse([-180, 480, 460, 1000], fill=RED + (25,))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(base.convert("RGBA"), glow)


def rounded_image(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width - 1, img.height - 1], radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def make_screenshot(height=600):
    shot = Image.open(SHOT_PATH).convert("RGB")
    scale = height / shot.height
    size = (max(1, round(shot.width * scale)), height)
    shot = shot.resize(size, Image.Resampling.LANCZOS)
    return rounded_image(shot, 16), scale


BG_IMAGE = make_background()
SHOT_RGBA, SHOT_SCALE = make_screenshot(600)
SHOT_X, SHOT_Y = 650, 60

# Original screenshot coordinates of interesting buttons / chat areas.
HIGHLIGHTS = {
    "market": (365, 171, 478, 199),
    "check": (30, 205, 134, 234),
    "chart": (38, 404, 340, 779),
    "stocks": (550, 171, 632, 199),
}


def map_rect(rect, ox=SHOT_X, oy=SHOT_Y, scale=SHOT_SCALE):
    x0, y0, x1, y1 = rect
    return (ox + x0 * scale, oy + y0 * scale,
            ox + x1 * scale, oy + y1 * scale)


def paste_screenshot(frame, t, intro=False, outro=False):
    """Place the app window with a shadow and a little movement."""
    if intro:
        slide = ease_out_cubic(min(1.0, t / 1.2))
        x = lerp(W + 40, SHOT_X, slide)
        y = SHOT_Y
    elif outro:
        x, y = SHOT_X, SHOT_Y
    else:
        x = SHOT_X
        y = SHOT_Y + math.sin(t * 0.8) * 3

    if outro:
        dim = SHOT_RGBA.copy()
        alpha = dim.getchannel("A").point(lambda v: int(v * 0.14))
        dim.putalpha(alpha)
    else:
        dim = SHOT_RGBA

    shadow = Image.new("RGBA", (dim.width + 40, dim.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [20, 24, dim.width + 18, dim.height + 28], radius=20,
        fill=(0, 0, 0, 135))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    frame.alpha_composite(shadow, (int(x) - 20, int(y) - 20))
    frame.alpha_composite(dim, (int(x), int(y)))
    return x, y


def draw_pill(draw, x, y, text, fg, border, fill=(18, 29, 49, 220), pad=14):
    f = font(18, "bold")
    box = draw.textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    draw.rounded_rectangle([x, y, x + w + pad * 2, y + h + pad],
                           radius=(h + pad) // 2, fill=fill,
                           outline=border, width=2)
    draw.text((x + pad, y + pad // 2 - 1), text, font=f, fill=fg)
    return w + pad * 2


def draw_code_pill(frame, x, y, text, colour):
    f = font(21, "mono")
    tmp = ImageDraw.Draw(frame)
    box = tmp.textbbox((0, 0), text, font=f)
    w = box[2] - box[0] + 40
    h = 48
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x, y, x + w, y + h], radius=12,
                        fill=(13, 23, 40, 230), outline=colour + (170,), width=2)
    d.text((x + 20, y + 11), text, font=f, fill=colour)
    frame.alpha_composite(layer)


def draw_alert_card(frame, x, y, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x, y, x + 480, y + 166], radius=16,
                        fill=(127, 29, 29, int(225 * alpha)),
                        outline=(255, 120, 120, int(210 * alpha)), width=2)
    d.text((x + 24, y + 20), "BIG DROP ALERT", font=font(19, "bold"),
           fill=(254, 226, 226, int(255 * alpha)))
    d.text((x + 24, y + 58), "TATASTEEL is down 8.4% today.",
           font=font(25, "bold"), fill=(255, 255, 255, int(255 * alpha)))
    d.text((x + 24, y + 102), "Don't panic. Open Stock Buddy and",
           font=font(18, "regular"), fill=(254, 226, 226, int(230 * alpha)))
    d.text((x + 24, y + 126), "type the name to see what is going on.",
           font=font(18, "regular"), fill=(254, 226, 226, int(230 * alpha)))
    frame.alpha_composite(layer)


def draw_highlight(frame, rect, colour, t):
    x0, y0, x1, y1 = rect
    pulse = 0.5 + 0.5 * math.sin(t * 5.0)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for extra, a in ((12, 35), (6, 70), (0, 255)):
        d.rounded_rectangle([x0 - extra, y0 - extra, x1 + extra, y1 + extra],
                            radius=12 + extra, outline=colour + (a,),
                            width=4 if extra == 0 else 3)
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        fill=colour + (int(25 + pulse * 25),))
    frame.alpha_composite(layer)


def text_layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def draw_scene_text(frame, kicker, headline, body, colour, alpha, y=145):
    if alpha <= 0:
        return
    layer = text_layer()
    d = ImageDraw.Draw(layer)
    slide = int((1 - ease_out_cubic(alpha)) * 22)
    a = int(255 * alpha)

    d.text((60, y + 10 + slide), kicker, font=font(18, "bold"),
           fill=colour + (a,))
    d.text((60, y + 46 + slide), headline, font=font(43, "bold"),
           fill=TEXT + (a,))
    d.multiline_text((60, y + 112 + slide), body, font=font(22, "regular"),
                     fill=MUTED + (a,), spacing=8)
    frame.alpha_composite(layer)


def draw_outro(frame, t):
    alpha = ease_out_cubic(min(1.0, max(0.0, (t - 19.2) / 0.7)))
    if alpha <= 0:
        return
    layer = text_layer()
    d = ImageDraw.Draw(layer)
    a = int(255 * alpha)
    y = int(lerp(245, 220, alpha))

    title_f = font(68, "bold")
    one = "STOCK "
    two = "BUDDY"
    w1 = d.textlength(one, font=title_f)
    w2 = d.textlength(two, font=title_f)
    x = (W - (w1 + w2)) / 2
    d.text((x, y), one, font=title_f, fill=TEXT + (a,))
    d.text((x + w1, y), two, font=title_f, fill=SKY + (a,))

    d.text((W / 2, y + 92), "Indian stocks, explained simply.",
           font=font(29, "regular"), fill=MUTED + (a,), anchor="ma")

    pills = [("Free", GREEN), ("Open source", BLUE), ("Windows", PURPLE)]
    total = 0
    widths = []
    for text, colour in pills:
        box = d.textbbox((0, 0), text, font=font(17, "bold"))
        width = box[2] - box[0] + 34
        widths.append(width)
        total += width + 12
    total -= 12
    px = (W - total) / 2
    for (text, colour), width in zip(pills, widths):
        d.rounded_rectangle([px, y + 158, px + width, y + 196],
                            radius=19, fill=(18, 29, 49, int(220 * alpha)),
                            outline=colour + (a,), width=2)
        d.text((px + width / 2, y + 167), text, font=font(17, "bold"),
               fill=colour + (a,), anchor="ma")
        px += width + 12

    d.text((W / 2, y + 250), "github.com/namish123chandra-prog/stock-reader",
           font=font(24, "mono"), fill=SKY + (a,), anchor="ma")
    d.text((W / 2, y + 300), "Learning helper, not financial advice.",
           font=font(17, "regular"), fill=MUTED + (int(210 * alpha),),
           anchor="ma")
    frame.alpha_composite(layer)


# ---- scenes: (start, end, kicker, headline, body, accent, highlight) ----
SCENES = [
    (3.4, 6.6, "01  ·  LIVE DATA",
     "Real NSE prices.",
     "In rupees. In India time.\nNo jargon, no paid feed.",
     GREEN, "market"),
    (6.6, 9.8, "02  ·  PLAIN ENGLISH",
     "BUY, WAIT or AVOID.",
     "Every answer explains why,\nplus the risks to watch.",
     BLUE, "check"),
    (9.8, 13.0, "03  ·  CHARTS",
     "See the shape fast.",
     "Type a stock name and get\na 30-day chart in chat.",
     TEAL, "chart"),
    (13.0, 16.2, "04  ·  ALERTS",
     "It watches for you.",
     "Big drops trigger a loud alert\non your laptop or phone.",
     RED, None),
    (16.2, 19.4, "05  ·  MEMORY",
     "It remembers your stocks.",
     "Tell it what you bought.\nGet a daily report card.",
     ORANGE, "stocks"),
]


def frame_at(t):
    frame = BG_IMAGE.copy()

    # Soft floating dots.
    rng = random.Random(42)
    dots = [(rng.randint(0, W), rng.randint(0, H), rng.randint(1, 3),
             rng.choice([BLUE, SKY, GREEN, PURPLE, ORANGE]))
            for _ in range(28)]
    dot_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dot_layer)
    for i, (x, y, r, colour) in enumerate(dots):
        yy = (y + math.sin(t * 0.35 + i) * 12) % H
        dd.ellipse([x - r, yy - r, x + r, yy + r], fill=colour + (55,))
    frame.alpha_composite(dot_layer)

    if t < 3.4:
        paste_screenshot(frame, t, intro=True)
        alpha = scene_alpha(t, 0.0, 3.4, 0.55)
        if alpha > 0:
            layer = text_layer()
            d = ImageDraw.Draw(layer)
            a = int(255 * alpha)
            slide = int((1 - ease_out_cubic(alpha)) * 24)

            # Colour bar
            bar_y = 232 + slide
            for i, colour in enumerate((BLUE, PURPLE, GREEN)):
                d.rounded_rectangle([60 + i * 74, bar_y, 60 + i * 74 + 62,
                                     bar_y + 6], radius=3, fill=colour + (a,))

            title_f = font(64, "bold")
            y = 266 + slide
            d.text((60, y), "STOCK", font=title_f, fill=TEXT + (a,))
            w1 = d.textlength("STOCK", font=title_f)
            d.text((60 + w1 + 18, y), "BUDDY", font=title_f, fill=SKY + (a,))
            d.text((60, y + 90), "Indian stocks, explained simply.",
                   font=font(28, "regular"), fill=MUTED + (a,))
            d.multiline_text((60, y + 148),
                             "Prices, alerts, charts and a\nbeginner-friendly chat.",
                             font=font(21, "regular"), fill=MUTED + (a,),
                             spacing=8)
            draw_pill(d, 60, y + 236, "OPEN SOURCE  •  WINDOWS  •  FREE",
                      GREEN, GREEN + (a,), fill=(18, 29, 49, int(220 * alpha)))
            frame.alpha_composite(layer)
        return frame

    if t >= 19.4:
        paste_screenshot(frame, t, outro=True)
        # Dark overlay so the end card stays readable.
        overlay = Image.new("RGBA", (W, H), (8, 13, 23, 170))
        frame.alpha_composite(overlay)
        draw_outro(frame, t)
        return frame

    # Feature scenes.
    for start, end, kicker, headline, body, colour, highlight in SCENES:
        if start <= t < end:
            paste_screenshot(frame, t)
            if highlight:
                draw_highlight(frame, map_rect(HIGHLIGHTS[highlight]),
                               colour, t - start)
            alpha = scene_alpha(t, start, end)
            draw_scene_text(frame, kicker, headline, body, colour, alpha)

            if kicker.startswith("03"):
                draw_code_pill(frame, 60, 440, "chart reliance", TEAL)
            elif kicker.startswith("05"):
                draw_code_pill(frame, 60, 440, "I bought 5 reliance at 1350",
                               ORANGE)
            elif kicker.startswith("04"):
                draw_alert_card(frame, 60, 430, alpha)
            break

    return frame


def main():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(OUT_PATH, fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise SystemExit("Could not open the video writer.")

    for i in range(FRAMES):
        t = i / FPS
        frame = frame_at(t)
        writer.write(cv2.cvtColor(np.array(frame.convert("RGB")),
                                  cv2.COLOR_RGB2BGR))
        if i % 60 == 0:
            print(f"frame {i}/{FRAMES}")

    writer.release()
    size = os.path.getsize(OUT_PATH) / (1024 * 1024)
    print(f"Saved {OUT_PATH} ({size:.1f} MB, {DURATION:.0f}s)")


if __name__ == "__main__":
    main()
