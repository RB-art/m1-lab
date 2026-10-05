"""CR-1: personas koda pārbaude iesniegumā (POST /submissions · personalCode)."""

from datetime import date
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
ISSUES = ["REQUIRED", "INVALID_FORMAT", "INVALID_DATE", "INVALID_CHECKSUM"]
WEIGHTS = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CENTURIES = {"0": 1800, "1": 1900, "2": 2000}
MISSING = object()

# Pieņemšanas kritēriji no tracker/CR-1.md:
# (Nr., ievade, HTTP statuss, saglabātā vērtība vai None, issue kods vai None)
ACCEPTANCE = [
    (1, "32000000001", 201, "32000000001", None),
    (2, "320000-00001", 201, "32000000001", None),
    (3, " 32000000001 ", 201, "32000000001", None),
    (4, "3200000000", 400, None, "INVALID_FORMAT"),
    (5, "320000000011", 400, None, "INVALID_FORMAT"),
    (6, "32000000O01", 400, None, "INVALID_FORMAT"),
    (7, MISSING, 400, None, "REQUIRED"),
    (8, "311299-21233", 201, "31129921233", None),
    (9, "3200-0000001", 400, None, "INVALID_FORMAT"),
    (10, "311299-21230", 400, None, "INVALID_CHECKSUM"),
    (11, "310299-12348", 400, None, "INVALID_DATE"),
]


def check_personal_code(value: object) -> tuple[str | None, str | None]:
    """Līgumā aprakstīto noteikumu atsauces īstenojums: (normalizēts kods, kļūda)."""
    if value is MISSING:
        return None, "REQUIRED"

    code = str(value).strip()
    if len(code) == 12 and code[6] == "-":
        code = code[:6] + code[7:]
    if len(code) != 11 or not (code.isascii() and code.isdigit()):
        return None, "INVALID_FORMAT"
    if code.startswith("32"):
        return code, None

    century = CENTURIES.get(code[6])
    try:
        if century is None:
            raise ValueError(code[6])
        date(century + int(code[4:6]), int(code[2:4]), int(code[0:2]))
    except ValueError:
        return None, "INVALID_DATE"

    check = (1101 - sum(w * int(d) for w, d in zip(WEIGHTS, code))) % 11
    if check == 10 or check != int(code[10]):
        return None, "INVALID_CHECKSUM"
    return code, None


@pytest.fixture(scope="module")
def document() -> dict:
    with (ROOT / "docs" / "openapi.yaml").open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def validation_error_details(document: dict) -> list[dict]:
    """Visas `VALIDATION_ERROR` piemēru `details` rindas no līguma."""
    media = document["components"]["responses"]["ValidationError"]["content"][
        "application/json"
    ]
    return [
        detail
        for example in media["examples"].values()
        if example["value"]["error"]["code"] == "VALIDATION_ERROR"
        for detail in example["value"]["error"]["details"]
    ]


@pytest.mark.parametrize(
    ("value", "status", "stored", "issue"),
    [pytest.param(*rest, id=f"AC{row}") for row, *rest in ACCEPTANCE],
)
def test_acceptance_criteria(
    document: dict, value: object, status: int, stored: str | None, issue: str | None
) -> None:
    actual_stored, actual_issue = check_personal_code(value)
    actual_status = 201 if actual_issue is None else 400
    responses = document["paths"]["/submissions"]["post"]["responses"]

    # Statuss, issue kods un saglabātā (normalizētā) vērtība; None = netiek saglabāts.
    assert actual_status == status
    assert actual_issue == issue
    assert actual_stored == stored

    # Līgums apraksta šo atbildi POST /submissions.
    assert str(status) in responses
    if status == 201:
        assert stored.isascii() and stored.isdigit() and len(stored) == 11
        assert responses["201"]["content"]["application/json"]["schema"]["$ref"] == (
            "#/components/schemas/SubmissionCreated"
        )
    else:
        assert responses["400"]["$ref"] == "#/components/responses/ValidationError"
        assert {"field": "personalCode", "issue": issue} in validation_error_details(document)


def test_personal_code_is_required(document: dict) -> None:
    create = document["components"]["schemas"]["SubmissionCreate"]

    assert "personalCode" in create["required"]
    assert create["properties"]["personalCode"]["type"] == "string"


def test_personal_code_has_no_pattern_so_server_can_normalize(document: dict) -> None:
    # Atstarpes un defise ir pieļaujamas ievadē, tāpēc shēmas pattern tās noraidītu.
    personal_code = document["components"]["schemas"]["SubmissionCreate"]["properties"][
        "personalCode"
    ]

    assert "pattern" not in personal_code


def test_personal_code_description_documents_rules(document: dict) -> None:
    description = document["components"]["schemas"]["SubmissionCreate"]["properties"][
        "personalCode"
    ]["description"]

    for issue in ISSUES:
        assert f"`{issue}`" in description
    assert "1, 6, 3, 7, 9, 10, 5, 8, 4, 2" in description
    assert "1101" in description
    assert "`32`" in description


def test_submission_returns_validation_error(document: dict) -> None:
    responses = document["paths"]["/submissions"]["post"]["responses"]

    assert responses["400"]["$ref"] == "#/components/responses/ValidationError"


def test_validation_error_has_example_per_personal_code_issue(document: dict) -> None:
    media = document["components"]["responses"]["ValidationError"]["content"][
        "application/json"
    ]
    details = validation_error_details(document)

    assert media["schema"]["$ref"] == "#/components/schemas/Error"
    assert {d["issue"] for d in details if d["field"] == "personalCode"} == set(ISSUES)
