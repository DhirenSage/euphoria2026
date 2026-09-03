"""Email-client-safe EUPHORIA transactional pass templates."""

from html import escape

SAGE_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png"
EUPHORIA_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png"


def pass_email_html(data: dict, pass_url: str) -> str:
    participant = escape(data["participant_name"])
    event_name = escape(data["event_name"])
    registration_id = escape(data["registration_id"])
    category = escape(data["category_name"])
    event_date = escape(data["event_date"])
    event_time = escape(data.get("event_time", "As per event schedule"))
    venue = escape(data["venue"])
    payment = escape(data.get("payment_status", "verified").replace("_", " ").upper())
    url = escape(pass_url, quote=True)
    return f"""<!doctype html>
<html><body style="margin:0;padding:0;background:#EEF2F7;font-family:Arial,Helvetica,sans-serif;color:#0F172A">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#EEF2F7"><tr><td align="center" style="padding:28px 12px">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:100%;max-width:600px;background:#FFFFFF;border-radius:18px;overflow:hidden;box-shadow:0 12px 40px rgba(15,23,42,.12)">
<tr><td style="height:9px;background:#FF007A;background-image:linear-gradient(90deg,#FF007A,#7928CA,#06B6D4,#F59E0B)"></td></tr>
<tr><td style="padding:24px 28px;background:#FFFFFF"><table role="presentation" width="100%"><tr>
<td valign="middle"><img src="{SAGE_LOGO}" width="150" alt="SAGE University Indore" style="display:block;max-width:150px;height:auto"></td>
<td align="right" valign="middle"><img src="{EUPHORIA_LOGO}" width="105" alt="EUPHORIA" style="display:inline-block;max-width:105px;height:auto"></td>
</tr></table></td></tr>
<tr><td style="padding:38px 30px;background:#0F172A;color:#FFFFFF">
<span style="display:inline-block;padding:7px 11px;border-radius:999px;background:#FF007A;color:#FFFFFF;font-size:11px;font-weight:bold;letter-spacing:1px">{category.upper()}</span>
<h1 style="margin:20px 0 10px;font-size:36px;line-height:1.08;letter-spacing:-1px;color:#FFFFFF">Your EUPHORIA<br>pass is ready!</h1>
<p style="margin:0;color:#CBD5E1;font-size:16px;line-height:1.65">Hello <strong style="color:#FFFFFF">{participant}</strong>, your registration is verified. Your complete printable pass is attached to this email.</p>
</td></tr>
<tr><td style="padding:28px 30px;background:#FFFFFF">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #E2E8F0;border-radius:12px">
<tr><td colspan="2" style="padding:18px;background:#F8FAFC;border-bottom:1px solid #E2E8F0"><span style="font-size:11px;color:#64748B;letter-spacing:1px">EVENT</span><br><strong style="font-size:21px;line-height:1.4;color:#0F172A">{event_name}</strong></td></tr>
<tr><td width="50%" style="padding:16px;border-right:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0"><span style="font-size:10px;color:#64748B;letter-spacing:1px">REGISTRATION ID</span><br><strong style="font-size:14px;line-height:1.8">{registration_id}</strong></td><td width="50%" style="padding:16px;border-bottom:1px solid #E2E8F0"><span style="font-size:10px;color:#64748B;letter-spacing:1px">PAYMENT / PASS</span><br><strong style="font-size:14px;line-height:1.8;color:#047857">{payment} · ACTIVE</strong></td></tr>
<tr><td width="50%" style="padding:16px;border-right:1px solid #E2E8F0"><span style="font-size:10px;color:#64748B;letter-spacing:1px">DATE &amp; TIME</span><br><strong style="font-size:14px;line-height:1.6">{event_date}<br>{event_time}</strong></td><td width="50%" style="padding:16px"><span style="font-size:10px;color:#64748B;letter-spacing:1px">VENUE</span><br><strong style="font-size:14px;line-height:1.6">{venue}</strong></td></tr>
</table>
<table role="presentation" width="100%"><tr><td align="center" style="padding:28px 0 12px"><a href="{url}" style="display:inline-block;min-width:230px;padding:16px 24px;background:#FF007A;color:#FFFFFF;text-decoration:none;border-radius:9px;font-size:15px;font-weight:bold">View secure digital pass&nbsp; →</a></td></tr></table>
<table role="presentation" width="100%" style="margin-top:18px;background:#FFF7ED;border-left:4px solid #F59E0B"><tr><td style="padding:16px 18px;color:#7C2D12;font-size:13px;line-height:1.6"><strong>Complete PDF pass attached</strong><br>The attachment includes participant details, event information, entry instructions and the official scannable QR—not just a QR image.</td></tr></table>
<h3 style="margin:28px 0 10px;font-size:16px;color:#0F172A">Gate instructions</h3>
<ul style="margin:0;padding-left:20px;color:#475569;font-size:13px;line-height:1.8"><li>Keep the PDF or digital QR ready before reaching the gate.</li><li>Carry a valid institutional photo ID.</li><li>This pass is non-transferable and valid only for the registered event.</li><li>One entry is permitted per configured event day.</li></ul>
</td></tr>
<tr><td style="padding:22px 30px;background:#0F172A;color:#94A3B8;font-size:11px;line-height:1.7;text-align:center">SAGE University Indore · EUPHORIA 2026<br>Need help? Reply to this email or contact the EUPHORIA Event Desk.</td></tr>
</table></td></tr></table></body></html>"""


def pass_email_text(data: dict, pass_url: str) -> str:
    return (
        f"Hello {data['participant_name']},\n\nYour EUPHORIA 2026 event pass is ready.\n"
        f"Event: {data['event_name']}\nRegistration ID: {data['registration_id']}\n"
        f"Date: {data['event_date']}\nVenue: {data['venue']}\nSecure pass: {pass_url}\n\n"
        "Your complete printable PDF pass is attached. Keep its QR ready at the entry gate."
    )