from pathlib import Path

from fastapi.testclient import TestClient

from main import (
    app,
    STORAGE_DIR,
    build_analysis_text,
    build_text_from_data,
)


client = TestClient(app)


# ===== ЮНИТ-ТЕСТЫ ШАБЛОНОВ =====

def test_build_analysis_text_basic():
    """
    Проверяем, что текст для ANALYSIS_RESULT:
    - содержит имя пациента
    - содержит гемоглобин и заключение
    - НЕ содержит id
    """
    data = {
        "analysis": {
            "id": "123",
            "patient_name": "Иванов Иван",
            "hemoglobin": 130,
            "conclusion": "Все ок",
            "date": "2025-11-21",
        }
    }

    text = build_analysis_text(data)

    assert text is not None
    assert "Иванов Иван" in text
    assert "Гемоглобин: 130" in text
    assert "Все ок" in text
    # id не должен попадать в документ
    assert "123" not in text


def test_build_text_from_data_for_analysis_template():
    """
    Проверяем, что build_text_from_data для шаблона ANALYSIS_RESULT
    использует красивый шаблон, а не сырой JSON.
    """
    data = {
        "analysis": {
            "id": "999",
            "patient_name": "Петров Петр",
            "hemoglobin": 140,
            "conclusion": "Небольшое отклонение",
        }
    }

    text = build_text_from_data("ANALYSIS_RESULT", data)

    # Заголовок
    assert "РЕЗУЛЬТАТ ЛАБОРАТОРНОГО АНАЛИЗА" in text
    # Имя пациента есть
    assert "Петров Петр" in text
    # id снова не должен появиться
    assert "999" not in text


def test_build_text_from_data_default_template():
    """
    Для других template_code должен использоваться режим с JSON.
    """
    data = {"foo": "bar"}
    text = build_text_from_data("SOME_OTHER_TEMPLATE", data)

    assert "Шаблон: SOME_OTHER_TEMPLATE" in text
    assert '"foo": "bar"' in text


# ===== API-ТЕСТЫ =====

def test_generate_document_creates_file(tmp_path, monkeypatch):
    """
    Тестируем POST /api/v1/documents:
    - возвращает 200
    - есть document_id и file_name
    - действительно создаётся файл на диске
    """

    # Подменим директорию хранения на временную, чтобы не мусорить
    monkeypatch.setattr("main.STORAGE_DIR", Path(tmp_path))

    # после подмены нужно обновить client, чтобы FastAPI увидел новое значение
    from main import app as fresh_app  # noqa: WPS433
    local_client = TestClient(fresh_app)

    payload = {
        "template_code": "ANALYSIS_RESULT",
        "format": "PDF",
        "data": {
            "analysis": {
                "id": "123",
                "patient_name": "Иванов Иван",
                "hemoglobin": 130,
                "conclusion": "Все ок",
                "date": "2025-11-21",
            }
        },
    }

    response = local_client.post("/api/v1/documents", json=payload)
    assert response.status_code == 200

    body = response.json()
    document_id = body["document_id"]
    file_name = body["file_name"]

    assert document_id
    assert file_name.endswith(".pdf")

    # Проверяем, что файл реально существует
    expected_file = Path(tmp_path) / file_name
    assert expected_file.exists()
    assert expected_file.stat().st_size > 0


def test_download_document_returns_content(tmp_path, monkeypatch):
    """
    Полный цикл:
    1) создаём документ
    2) скачиваем его
    Проверяем что:
    - /content отдаёт 200
    - контент не пустой
    - Content-Type корректный
    """

    # снова подменяем директорию хранения
    monkeypatch.setattr("main.STORAGE_DIR", Path(tmp_path))
    from main import app as fresh_app  # noqa: WPS433
    local_client = TestClient(fresh_app)

    payload = {
        "template_code": "ANALYSIS_RESULT",
        "format": "PDF",
        "data": {
            "analysis": {
                "id": "123",
                "patient_name": "Иванов Иван",
                "hemoglobin": 130,
                "conclusion": "Все ок",
            }
        },
    }

    create_resp = local_client.post("/api/v1/documents", json=payload)
    assert create_resp.status_code == 200
    document_id = create_resp.json()["document_id"]

    # Скачиваем
    download_resp = local_client.get(f"/api/v1/documents/{document_id}/content")
    assert download_resp.status_code == 200
    assert download_resp.content  # не пустой
    assert (
        download_resp.headers["content-type"] == "application/pdf"
    )


def test_download_document_not_found():
    """
    Если документа нет, должны получить 404.
    """
    resp = client.get("/api/v1/documents/non-existing-id/content")
    assert resp.status_code == 404
