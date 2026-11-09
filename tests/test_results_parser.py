"""Pruebas del parser de resultados (parser/results_parser.py).

Cubren los bugs encontrados durante el proyecto:
- testng-results.xml: atributo 'failed' (no 'failures'), duration-ms por
  <suite>, exclusion de is-config, classname del <class> padre.
- XML estilo JUnit: <failure> sin hijos no debe perderse (bug de
  `find(...) or find(...)`), estados passed/failed/skipped, fusion de
  multiples TEST-*.xml, deduplicacion por (project, executed_at).
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parser.results_parser import (  # noqa: E402
    append_to_store,
    build_record,
    parse_junit_xml,
    parse_reports_dir,
    parse_testng_results,
)
from tests.fixtures_xml import (  # noqa: E402
    JUNIT_FAILURE_XML,
    JUNIT_MISMATCH_XML,
    JUNIT_PASSED_XML,
    JUNIT_SKIPPED_XML,
    TESTNG_XML,
)


@pytest.fixture
def testng_file(tmp_path):
    path = tmp_path / "testng-results.xml"
    path.write_text(TESTNG_XML, encoding="utf-8")
    return path


@pytest.fixture
def junit_dir(tmp_path):
    (tmp_path / "TEST-tests.LoginTest.xml").write_text(JUNIT_PASSED_XML, encoding="utf-8")
    (tmp_path / "TEST-tests.NavigationTest.xml").write_text(JUNIT_FAILURE_XML, encoding="utf-8")
    (tmp_path / "TEST-tests.SwipeTest.xml").write_text(JUNIT_SKIPPED_XML, encoding="utf-8")
    return tmp_path


class TestParseTestngResults:
    def test_totals_from_root_attributes(self, testng_file):
        result = parse_testng_results(testng_file)
        assert result["total"] == 3
        assert result["passed"] == 2
        assert result["failed"] == 1
        assert result["skipped"] == 0

    def test_duration_from_suites_not_root(self, testng_file):
        # duration-ms vive en <suite>, no en el raíz (bug corregido)
        result = parse_testng_results(testng_file)
        assert result["duration_ms"] == 12345

    def test_config_methods_excluded(self, testng_file):
        result = parse_testng_results(testng_file)
        names = [t["name"] for t in result["tests"]]
        assert "setUp" not in names and "tearDown" not in names
        assert len(result["tests"]) == 3

    def test_classname_from_parent_class(self, testng_file):
        result = parse_testng_results(testng_file)
        assert all(t["class"] == "tests.LoginTest" for t in result["tests"])

    def test_exception_captured(self, testng_file):
        result = parse_testng_results(testng_file)
        failed = next(t for t in result["tests"] if t["status"] == "failed")
        assert failed["exception_type"] == "java.lang.AssertionError"
        assert "expected [true]" in failed["exception_message"]


class TestParseJunitXml:
    def test_failure_without_children_is_registered(self, tmp_path):
        # Bug original: <failure> sin hijos evalua False y el fallo se perdia
        path = tmp_path / "TEST-x.xml"
        path.write_text(JUNIT_FAILURE_XML, encoding="utf-8")
        result = parse_junit_xml(path)
        assert result["failed"] == 1
        assert result["tests"][0]["status"] == "failed"
        assert "expected [true]" in result["tests"][0]["exception_message"]

    def test_passed_case(self, tmp_path):
        path = tmp_path / "TEST-x.xml"
        path.write_text(JUNIT_PASSED_XML, encoding="utf-8")
        result = parse_junit_xml(path)
        assert result["passed"] == 1 and result["failed"] == 0

    def test_skipped_case(self, tmp_path):
        path = tmp_path / "TEST-x.xml"
        path.write_text(JUNIT_SKIPPED_XML, encoding="utf-8")
        result = parse_junit_xml(path)
        assert result["skipped"] == 1
        assert result["tests"][0]["status"] == "skipped"

    def test_counts_real_testcases(self, tmp_path):
        # El detalle debe tener los testcase reales (2), no el atributo tests=2
        # mal usado: aqui coinciden, pero el detalle manda sobre el agregado.
        path = tmp_path / "TEST-x.xml"
        path.write_text(JUNIT_MISMATCH_XML, encoding="utf-8")
        result = parse_junit_xml(path)
        assert len(result["tests"]) == 2
        assert result["failed"] == 1


class TestParseReportsDir:
    def test_prefers_testng_results(self, tmp_path):
        (tmp_path / "testng-results.xml").write_text(TESTNG_XML, encoding="utf-8")
        result = parse_reports_dir(tmp_path)
        assert result["total"] == 3

    def test_merges_multiple_junit_files(self, junit_dir):
        result = parse_reports_dir(junit_dir)
        # 3 archivos TEST-*.xml: 1 passed + 1 failed + 1 skipped
        assert result["total"] == 3
        assert result["passed"] == 1
        assert result["failed"] == 1
        assert result["skipped"] == 1
        assert len(result["tests"]) == 3

    def test_raises_without_reports(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_reports_dir(tmp_path)


class TestAppendToStore:
    def test_dedup_by_project_and_executed_at(self, tmp_path):
        store_path = tmp_path / "results.json"
        record = {"project": "X", "executed_at": "2026-11-09T15:00:00+00:00",
                  "total": 2, "passed": 1, "failed": 1, "skipped": 0,
                  "success_rate": 50.0, "duration_ms": 100, "tests": []}
        append_to_store(store_path, record)
        # misma clave: debe reemplazar, no duplicar
        record2 = dict(record, passed=2, success_rate=100.0)
        append_to_store(store_path, record2)
        store = json.loads(store_path.read_text(encoding="utf-8"))
        assert len(store) == 1
        assert store[0]["passed"] == 2

    def test_different_keys_coexist(self, tmp_path):
        store_path = tmp_path / "results.json"
        base = {"total": 1, "passed": 1, "failed": 0, "skipped": 0,
                "success_rate": 100.0, "duration_ms": 100, "tests": []}
        append_to_store(store_path, dict(base, project="A", executed_at="2026-11-09T15:00:00+00:00"))
        append_to_store(store_path, dict(base, project="B", executed_at="2026-11-09T15:00:00+00:00"))
        append_to_store(store_path, dict(base, project="A", executed_at="2026-11-09T16:00:00+00:00"))
        store = json.loads(store_path.read_text(encoding="utf-8"))
        assert len(store) == 3
