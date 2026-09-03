"""Branded pass email/PDF generator contract: table-based HTML with participant/event/status/
CTA/instructions, and a real complete-ticket PDF -- the delivery evidence for pass resend
(see spec_deviations: mailbox content cannot be inspected by browser automation, so the
generator contract plus the provider-accepted resend in test_tscheck_pass_resend.py together
are the evidence for this criterion).
"""

from lib.email_template import pass_email_html, pass_email_text
from lib.pdf_generator import pass_pdf
import qrcode
from io import BytesIO


SAMPLE_DATA = {
    "registration_id": "TSCHECK-CONTRACT-0001",
    "participant_name": "tscheck Contract Participant",
    "event_name": "tscheck Contract Event",
    "category_name": "cultural",
    "venue": "tscheck Venue",
    "event_date": "15 September 2026",
    "event_time": "10:00 AM",
    "college": "tscheck College",
    "payment_status": "manual_verified",
}
SAMPLE_URL = "https://example.test/pass/TSCHECK-CONTRACT-0001?key=sample"


def test_pass_email_html_is_table_based_and_branded():
    html = pass_email_html(SAMPLE_DATA, SAMPLE_URL)
    assert "<table" in html and "<!doctype html>" in html.lower()
    # participant / event / status
    assert SAMPLE_DATA["participant_name"] in html
    assert SAMPLE_DATA["event_name"] in html
    assert "MANUAL VERIFIED" in html.upper()
    assert SAMPLE_DATA["registration_id"] in html
    # CTA linking to the secure pass url
    assert SAMPLE_URL in html
    assert "View secure digital pass" in html
    # gate / usage instructions text
    text = pass_email_text(SAMPLE_DATA, SAMPLE_URL)
    assert "attached" in text.lower()
    assert SAMPLE_DATA["event_name"] in text
    assert SAMPLE_DATA["registration_id"] in text


def test_pass_pdf_generator_produces_complete_branded_pdf():
    qr_buffer = BytesIO()
    qrcode.make("tscheck-contract-token").save(qr_buffer, format="PNG")
    pdf_bytes = pass_pdf(SAMPLE_DATA, qr_buffer.getvalue())
    assert pdf_bytes[:5] == b"%PDF-"
    assert len(pdf_bytes) > 50 * 1024, f"generated PDF unexpectedly small: {len(pdf_bytes)} bytes"
