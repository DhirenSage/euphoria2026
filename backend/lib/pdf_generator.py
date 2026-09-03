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


def fitted_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int, bold: bool = True):
    size = start
    while size > minimum and draw.textlength(str(text), font=font(size, bold)) > max_width:
        size -= 2
    return font(size, bold)


def pass_image(data: dict, qr_bytes: bytes) -> Image.Image:
    width, height = 1200, 730
    canvas = Image.new("RGBA", (width, height), "#0D0F17")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((18, 18, 1182, 712), radius=25, fill="#151A26", outline="#475569", width=2)
    for x in range(20, 1180):
        ratio = (x - 20) / 1160
        stops = [(255, 0, 122), (121, 40, 202), (6, 182, 212), (245, 158, 11)]
        segment = min(2, int(ratio * 3)); local = ratio * 3 - segment
        first, second = stops[segment], stops[segment + 1]
        color = tuple(int(first[i] * (1 - local) + second[i] * local) for i in range(3))
        draw.line((x, 18, x, 28), fill=color)
    draw.rectangle((20, 28, 1180, 112), fill="#FFFFFF")
    paste_fit(canvas, remote_image(SAGE_LOGO), (48, 43, 300, 98))
    paste_fit(canvas, remote_image(EUPHORIA_LOGO), (335, 39, 500, 102))
    draw.rounded_rectangle((1045, 51, 1150, 87), radius=18, fill="#D1FAE5", outline="#6EE7B7", width=2)
    draw.ellipse((1062, 64, 1072, 74), fill="#10B981")
    draw.text((1082, 61), "ACTIVE", font=font(14, True), fill="#065F46")
    for y in range(112, 326):
        ratio = (y - 112) / 214
        start, end = (255, 0, 122), (79, 34, 194)
        color = tuple(int(start[i] * (1 - ratio) + end[i] * ratio) for i in range(3))
        draw.line((20, y, 800, y), fill=color)
    draw.ellipse((590, 65, 910, 380), outline="#FFFFFF38", width=3)
    draw.ellipse((675, 100, 850, 275), fill="#FFFFFF12")
    draw.text((52, 136), f"{data['category_name'].upper()}  ·  OFFICIAL EVENT PASS", font=font(21, True), fill="#FFE4F0")
    event_name = data["event_name"].upper()
    draw.text((52, 178), event_name, font=fitted_font(draw, event_name, 700, 64, 36), fill="#FFFFFF")
    draw.rounded_rectangle((52, 260, 277, 298), radius=19, fill="#17102A")
    draw.text((74, 270), "PARTICIPANT  /  2026", font=font(14, True), fill="#FFFFFF")
    draw.rectangle((20, 326, 800, 630), fill="#151A26")
    draw.text((52, 348), "THIS PASS BELONGS TO", font=font(18, True), fill="#22D3EE")
    participant = data["participant_name"].upper()
    draw.text((52, 378), participant, font=fitted_font(draw, participant, 700, 46, 30), fill="#FFFFFF")
    details = [
        ("REGISTRATION ID", data["registration_id"]),
        ("PAYMENT / PASS", f"{data.get('payment_status','VERIFIED').replace('_',' ').upper()} · ACTIVE"),
        ("DATE & TIME", f"{data['event_date']} · {data.get('event_time','As per schedule')}"),
        ("VENUE", data["venue"]),
        ("COLLEGE / INSTITUTION", data.get("college", "Registered participant")),
    ]
    for index, (label, value) in enumerate(details):
        if index < 4:
            column, row = index % 2, index // 2
            x, y, box_width = 52 + column * 360, 438 + row * 68, 342
        else:
            x, y, box_width = 52, 568, 702
        draw.rounded_rectangle((x, y, x + box_width, y + 60), radius=8, fill="#1D2533", outline="#334155", width=1)
        draw.text((x + 12, y + 7), label, font=font(14, True), fill="#94A3B8")
        draw.text((x + 12, y + 31), value, font=fitted_font(draw, value, box_width - 24, 22, 14), fill="#FFFFFF")
    draw.rectangle((800, 112, 1180, 630), fill="#FFFFFF")
    draw.text((990, 153), "SECURE ENTRY CODE", anchor="ma", font=font(17, True), fill="#FF007A")
    draw.text((990, 190), "Scan at authorized gate", anchor="ma", font=font(25, True), fill="#0F172A")
    security = hashlib.sha256(data["registration_id"].encode()).hexdigest()[:12].upper()
    draw.text((990, 220), f"#{security}", anchor="ma", font=font(15, True), fill="#64748B")
    qr = Image.open(BytesIO(qr_bytes)).convert("RGB").resize((290, 290), Image.Resampling.NEAREST)
    draw.rounded_rectangle((845, 250, 1135, 540), radius=18, fill="#FFFFFF", outline="#0F172A", width=3)
    canvas.paste(qr, (845, 250))
    draw.text((990, 565), "PURE BLACK-ON-WHITE QR", anchor="ma", font=font(14, True), fill="#64748B")
    draw.text((990, 592), "Keep screen brightness high", anchor="ma", font=font(16, True), fill="#0F172A")
    draw.rectangle((20, 630, 1180, 710), fill="#0A0E17")
    footer_items = [("01", "Carry valid institutional photo ID"), ("02", "Non-transferable; valid for this event only"), ("03", "One entry per configured event day")]
    for index, (number, text) in enumerate(footer_items):
        x = 42 + index * 386
        if index:
            draw.line((x - 18, 630, x - 18, 710), fill="#334155", width=2)
        draw.text((x, 643), number, font=font(17, True), fill="#F59E0B")
        draw.text((x, 674), text, font=fitted_font(draw, text, 335, 17, 13), fill="#E2E8F0")
    draw.line((800, 112, 800, 630), fill="#64748B", width=2)
    return canvas.convert("RGB")


def pass_pdf(data: dict, qr_bytes: bytes) -> bytes:
    canvas = pass_image(data, qr_bytes)
    output = BytesIO()
    canvas.save(output, format="PDF", resolution=150.0, quality=95, title=f"EUPHORIA Pass {data['registration_id']}")
    return output.getvalue()