"""Colourful mobile-ticket PDF generation using Pillow."""

from functools import lru_cache
from io import BytesIO
import hashlib
import random
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFont

SAGE_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png"
EUPHORIA_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)
    except OSError:
        return ImageFont.load_default()


@lru_cache(maxsize=4)
def remote_image(url: str) -> Image.Image | None:
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception:
        return None


def paste_fit(canvas: Image.Image, source: Image.Image | None, box: tuple[int, int, int, int]):
    if source is None:
        return
    x1, y1, x2, y2 = box
    item = source.copy()
    item.thumbnail((x2 - x1, y2 - y1), Image.Resampling.LANCZOS)
    canvas.alpha_composite(item, (x1 + (x2 - x1 - item.width) // 2, y1 + (y2 - y1 - item.height) // 2))


def wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, text_font, fill, spacing=8, max_lines=3):
    average = max(8, int(draw.textlength("ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=text_font) / 26))
    lines = textwrap.wrap(str(text), width=max(5, width // average))[:max_lines] or [""]
    draw.multiline_text(xy, "\n".join(lines), font=text_font, fill=fill, spacing=spacing)


def pass_pdf(data: dict, qr_bytes: bytes) -> bytes:
    width, height = 1000, 2100
    canvas = Image.new("RGBA", (width, height), "#0D0F17")
    draw = ImageDraw.Draw(canvas)
    palette = ["#FF007A", "#7928CA", "#06B6D4", "#F59E0B"]
    for y in range(0, 430):
        ratio = y / 430
        color = (int(255 * (1 - ratio) + 121 * ratio), int(0 * (1 - ratio) + 40 * ratio), int(122 * (1 - ratio) + 202 * ratio))
        draw.line((0, y, width, y), fill=color)
    seed = int(hashlib.sha256(data["registration_id"].encode()).hexdigest()[:12], 16)
    random.seed(seed)
    for _ in range(80):
        x, y = random.randint(0, width), random.randint(0, 430)
        radius = random.randint(2, 13)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=palette[random.randrange(len(palette))] + "55")
    draw.rounded_rectangle((55, 52, 945, 2045), radius=34, fill="#161B26", outline="#334155", width=3)
    draw.rounded_rectangle((80, 78, 920, 240), radius=24, fill="#FFFFFF")
    paste_fit(canvas, remote_image(SAGE_LOGO), (105, 98, 425, 220))
    paste_fit(canvas, remote_image(EUPHORIA_LOGO), (665, 94, 890, 224))
    draw.text((110, 300), "EUPHORIA 2026  /  OFFICIAL EVENT PASS", font=font(24, True), fill="#FFE4F0")
    draw.rounded_rectangle((110, 355, 110 + min(470, 34 + len(data["category_name"]) * 20), 413), radius=29, fill="#FF007A")
    draw.text((132, 370), data["category_name"].upper(), font=font(22, True), fill="#FFFFFF")
    wrapped(draw, data["event_name"].upper(), (110, 455), 780, font(62, True), "#FFFFFF", spacing=5, max_lines=2)
    draw.text((110, 620), "PARTICIPANT", font=font(20, True), fill="#06B6D4")
    wrapped(draw, data["participant_name"].upper(), (110, 660), 780, font(50, True), "#FFFFFF", spacing=4, max_lines=2)
    details = [
        ("REGISTRATION ID", data["registration_id"]), ("PAYMENT / PASS", f"{data.get('payment_status','VERIFIED').replace('_',' ').upper()}  ·  ACTIVE"),
        ("DATE & TIME", f"{data['event_date']}\n{data.get('event_time','As per schedule')}"), ("VENUE", data["venue"]),
        ("COLLEGE / INSTITUTION", data.get("college", "Registered participant")), ("PASS TYPE", "EVENT PARTICIPANT"),
    ]
    top = 800
    for index, (label, value) in enumerate(details):
        column, row = index % 2, index // 2
        x, y = 110 + column * 395, top + row * 150
        draw.text((x, y), label, font=font(17, True), fill="#94A3B8")
        wrapped(draw, value, (x, y + 34), 345, font(25, True), "#F8FAFC", spacing=4, max_lines=2)
    separator_y = 1265
    draw.line((90, separator_y, 910, separator_y), fill="#475569", width=3)
    for x in range(105, 910, 35):
        draw.line((x, separator_y, min(x + 16, 910), separator_y), fill="#CBD5E1", width=3)
    draw.ellipse((-30, separator_y - 32, 34, separator_y + 32), fill="#0D0F17")
    draw.ellipse((966, separator_y - 32, 1030, separator_y + 32), fill="#0D0F17")
    draw.text((110, 1305), "SCAN AT AUTHORIZED GATE", font=font(22, True), fill="#F59E0B")
    qr = Image.open(BytesIO(qr_bytes)).convert("RGB").resize((390, 390), Image.Resampling.NEAREST)
    draw.rounded_rectangle((305, 1350, 695, 1740), radius=18, fill="#FFFFFF")
    canvas.paste(qr, (305, 1350))
    security = hashlib.sha256(data["registration_id"].encode()).hexdigest()[:12].upper()
    draw.text((500, 1762), f"SECURITY  {security}", anchor="ma", font=font(18, True), fill="#94A3B8")
    instructions = "VALID PHOTO ID REQUIRED  •  NON-TRANSFERABLE  •  ONE ENTRY PER CONFIGURED EVENT DAY  •  KEEP QR READY"
    wrapped(draw, instructions, (125, 1820), 750, font(18, True), "#CBD5E1", spacing=7, max_lines=3)
    draw.rounded_rectangle((110, 1940, 890, 2005), radius=32, fill="#10B981")
    draw.text((500, 1972), "VERIFIED  •  READY FOR ENTRY", anchor="mm", font=font(22, True), fill="#062817")
    output = BytesIO()
    canvas.convert("RGB").save(output, format="PDF", resolution=254.0, quality=95, title=f"EUPHORIA Pass {data['registration_id']}")
    return output.getvalue()