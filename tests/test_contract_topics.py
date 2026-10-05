"""CR-0: tēma PARKS un GET /topics līgumā."""

from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
ERROR_REF = "#/components/schemas/Error"
EXPECTED_TOPICS = [
    ("ROADS", "Ceļi un ielas"),
    ("WASTE", "Atkritumi"),
    ("PLANNING", "Teritorijas plānošana"),
    ("PARKS", "Parki un skvēri"),
    ("OTHER", "Cits"),
]


@pytest.fixture(scope="module")
def document() -> dict:
    with (ROOT / "docs" / "openapi.yaml").open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def test_topic_enum_has_parks_and_other_last(document: dict) -> None:
    enum = document["components"]["schemas"]["Topic"]["enum"]

    assert enum == [code for code, _ in EXPECTED_TOPICS]
    assert "ZOO" not in enum


def test_get_topics_returns_topic_list(document: dict) -> None:
    ok = document["paths"]["/topics"]["get"]["responses"]["200"]
    media = ok["content"]["application/json"]

    assert media["schema"]["type"] == "array"
    assert media["schema"]["items"]["$ref"] == "#/components/schemas/TopicItem"
    assert [(item["code"], item["name"]) for item in media["example"]] == EXPECTED_TOPICS


def test_topic_item_code_uses_topic_enum(document: dict) -> None:
    item = document["components"]["schemas"]["TopicItem"]

    assert set(item["required"]) == {"code", "name"}
    assert item["properties"]["code"]["$ref"] == "#/components/schemas/Topic"


@pytest.mark.parametrize("code", ["400", "404", "500"])
def test_get_topics_errors_use_shared_error_schema(document: dict, code: str) -> None:
    response = document["paths"]["/topics"]["get"]["responses"][code]

    assert response["content"]["application/json"]["schema"]["$ref"] == ERROR_REF


def test_submission_topic_is_validated_against_topic_enum(document: dict) -> None:
    create = document["components"]["schemas"]["SubmissionCreate"]
    operation = document["paths"]["/submissions"]["post"]

    assert create["properties"]["topic"]["$ref"] == "#/components/schemas/Topic"
    assert "topic" in create["required"]
    assert "400" in operation["responses"]
