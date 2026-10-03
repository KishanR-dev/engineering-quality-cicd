import json

from scripts.build_command_center import (
    get_projects_overview,
    get_quality_ci_data,
    get_traceability_data,
    get_transformation_data,
)


def test_projects_overview():
    projects = get_projects_overview()
    assert len(projects) == 5
    assert projects[-1]["name"] == "Command Center"
    assert projects[-1]["id"] == "P5"


def test_get_transformation_data_graceful_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("scripts.build_command_center.BENCHMARKS_DIR", tmp_path)
    data = get_transformation_data()
    assert data["status"] == "UNKNOWN"
    assert data["baseline"] is None
    assert data["transformed"] is None
    assert len(data["limitations"]) > 0


def test_get_traceability_data_graceful_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("scripts.build_command_center.TRACEABILITY_FILE", tmp_path / "missing.json")
    data = get_traceability_data()
    # If the file does not exist, status should be FAIL
    assert data["status"] == "FAIL"


def test_get_traceability_data_valid(monkeypatch, tmp_path):
    mock_file = tmp_path / "mock_traceability.json"
    mock_data = [
        {
            "id": "FR-001",
            "title": "Mock Req",
            "implementation_refs": ["file1.py"],
            "test_refs": ["test_file.py"],
            "evidence_refs": [],
        }
    ]
    with open(mock_file, "w") as f:
        json.dump(mock_data, f)

    monkeypatch.setattr("scripts.build_command_center.TRACEABILITY_FILE", mock_file)
    data = get_traceability_data()
    assert data["status"] == "PASS"
    assert data["total_requirements"] == 1
    assert data["covered_requirements"] == 1
    assert data["missing_evidence"] == 0
    assert len(data["requirements"]) == 1
    assert data["requirements"][0]["covered"] is True


def test_get_quality_ci_data_graceful_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("scripts.build_command_center.COVERAGE_FILE", tmp_path / "missing.xml")
    data = get_quality_ci_data()
    assert data["status"] == "STALE"
    assert data["test_coverage"] is None
