"""Backend/artifact coverage for production integration secret-safety.

Criterion: "Production integrations remain secret-safe" -- CodeIgniter reads
Easebuzz live key/salt and Google Workspace SMTP/App Password only from the
cPanel `.env` (never hardcoded); release/source ZIPs contain no `.env` file
and no real credentials; the shipped env template uses placeholder values;
and no live Easebuzz charge is attempted from this suite.

Inspects the release artifacts named in the briefing's seed_facts directly on
disk (no live server request needed for this criterion).
"""
import zipfile
from pathlib import Path

import pytest

RELEASES_DIR = Path("/app/releases")
SOURCE_ZIP = RELEASES_DIR / "euphoria-codeigniter-source.zip"
CPANEL_ZIP = RELEASES_DIR / "euphoria-cpanel-single-folder.zip"
INITIAL_SQL = RELEASES_DIR / "euphoria_initial.sql"

REQUIRED_ARTIFACTS = [SOURCE_ZIP, CPANEL_ZIP, INITIAL_SQL, RELEASES_DIR / "SHA256SUMS.txt"]


@pytest.fixture(scope="module", autouse=True)
def _artifacts_present():
    missing = [str(p) for p in REQUIRED_ARTIFACTS if not p.exists()]
    if missing:
        pytest.skip(f"release artifacts missing, skipping secret-safety checks: {missing}")


def _env_like_entries(zf: zipfile.ZipFile):
    return [
        name for name in zf.namelist()
        if name.rsplit("/", 1)[-1] == ".env" or name.endswith("/.env")
    ]


@pytest.mark.parametrize("zip_path", [SOURCE_ZIP, CPANEL_ZIP])
def test_release_zip_contains_no_real_env_file(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        real_env_entries = _env_like_entries(zf)
    assert not real_env_entries, (
        f"{zip_path.name} must not ship a real .env file, found: {real_env_entries}"
    )


@pytest.mark.parametrize("zip_path", [SOURCE_ZIP, CPANEL_ZIP])
def test_release_zip_env_template_uses_placeholders_not_real_credentials(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        template_entries = [
            name for name in zf.namelist()
            if name.rsplit("/", 1)[-1] in ("cpanel.env.example", "env.production.example")
            or name == "codeigniter/env"
        ]
        assert template_entries, f"{zip_path.name} should ship at least one env template/example file"
        for entry in template_entries:
            content = zf.read(entry).decode("utf-8", errors="replace")
            lower = content.lower()
            assert "easebuzz_key" in lower or "easebuzz" in lower, (
                f"{entry} in {zip_path.name} should reference the Easebuzz key setting"
            )
            # No plausible live-looking Easebuzz key/salt or SMTP app password: the shipped
            # template must use placeholder text, not a real secret value.
            assert "replace_with" in lower or "changeme" in lower or "your-" in lower or "example" in lower, (
                f"{entry} in {zip_path.name} does not look like a placeholder-only template"
            )


def test_no_zip_entry_path_is_a_literal_dotenv_anywhere_in_the_release_bundle():
    for zip_path in (SOURCE_ZIP, CPANEL_ZIP):
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                assert not info.filename.endswith("/.env"), f"{zip_path.name} contains {info.filename}"
                assert info.filename != ".env", f"{zip_path.name} contains {info.filename}"


def test_source_env_example_documents_env_only_production_secrets():
    """The source template's own .env / env.example must document that live
    Easebuzz/SMTP secrets are environment-only, never hardcoded in source."""
    candidates = [
        Path("/app/codeigniter/env"),
    ]
    existing = [p for p in candidates if p.exists()]
    assert existing, "expected a template env file under /app/codeigniter"
    combined = "\n".join(p.read_text() for p in existing)
    assert "EASEBUZZ" in combined.upper()
    assert "SMTP" in combined.upper()
    # The template's own committed env file ships test/local values, not a live
    # production Easebuzz environment flag or a filled-in credential.
    assert "EASEBUZZ_ENV = test" in combined or "EASEBUZZ_ENV=test" in combined
    env_values = {}
    for line in combined.splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        env_values[key.strip()] = value.strip().strip("'\"")
    assert env_values.get("EASEBUZZ_KEY") == ""
    assert env_values.get("EASEBUZZ_SALT") == ""
