from fastapi.testclient import TestClient
import pytest

from main import (
    app,
    notification_service,
    notifications_store,
    AnalysisResultEvent,
    NotificationStatus,
    RecipientType,
)


client = TestClient(app)


# ====== общая фикстура: очищаем хранилище перед каждым тестом ======

@pytest.fixture(autouse=True)
def clear_store():
    notifications_store.clear()
    yield
    notifications_store.clear()


# ================= ЮНИТ-ТЕСТЫ ДОМЕНА =================


def test_handle_result_added_creates_patient_notification():
    """
    RESULT_ADDED -> создаётся и отправляется уведомление пациенту.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-1",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Иванов Иван",
    )

    created = notification_service.handle_analysis_event(event)

    assert len(created) == 1
    notif = created[0]

    assert notif.recipient_type == RecipientType.PATIENT
    assert notif.recipient_email == "patient@example.com"
    assert notif.analysis_id == "a-1"
    assert notif.status == NotificationStatus.SENT
    assert "Результат вашего анализа" in notif.body

    # уведомление лежит в хранилище
    assert len(notifications_store) == 1
    assert notif.id in notifications_store


def test_handle_result_confirmed_creates_doctor_notification():
    """
    RESULT_CONFIRMED -> отправляем уведомление врачу.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_CONFIRMED",
        analysis_id="a-2",
        patient_email=None,
        doctor_email="doc@example.com",
        patient_name=None,
    )

    created = notification_service.handle_analysis_event(event)

    assert len(created) == 1
    notif = created[0]

    assert notif.recipient_type == RecipientType.DOCTOR
    assert notif.recipient_email == "doc@example.com"
    assert notif.analysis_id == "a-2"
    assert notif.status == NotificationStatus.SENT
    assert "подтверждён" in notif.body or "подтвержден" in notif.body.lower()


def test_handle_result_viewed_marks_notifications_read():
    """
    RESULT_VIEWED -> все уведомления по этому анализу для пациента становятся READ.
    """
    # сначала создаём уведомление для пациента
    event_added = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-3",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    created = notification_service.handle_analysis_event(event_added)
    notif = created[0]
    assert notif.status == NotificationStatus.SENT

    # теперь имитируем событие RESULT_VIEWED
    event_viewed = AnalysisResultEvent(
        event_type="RESULT_VIEWED",
        analysis_id="a-3",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    notification_service.handle_analysis_event(event_viewed)

    stored = notifications_store[notif.id]
    assert stored.status == NotificationStatus.READ


def test_mark_read_changes_status():
    """
    Команда 'Прочитать уведомление' меняет статус на READ.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-4",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    created = notification_service.handle_analysis_event(event)
    notif = created[0]

    updated = notification_service.mark_read(notif.id)

    assert updated.status == NotificationStatus.READ
    assert notifications_store[notif.id].status == NotificationStatus.READ


def test_mark_important_sets_flag():
    """
    Команда 'Отметить уведомление как важное' ставит флаг is_important.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-5",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    created = notification_service.handle_analysis_event(event)
    notif = created[0]

    updated = notification_service.mark_important(notif.id)

    assert updated.is_important is True
    assert notifications_store[notif.id].is_important is True


# ================= API-ТЕСТЫ =================


def test_test_event_endpoint_creates_notification():
    """
    POST /api/v1/notifications/test-event должен создавать уведомление.
    """
    payload = {
        "event_type": "RESULT_ADDED",
        "analysis_id": "a-6",
        "patient_email": "patient@example.com",
        "doctor_email": None,
        "patient_name": "Иван",
    }

    resp = client.post("/api/v1/notifications/test-event", json=payload)
    assert resp.status_code == 200
    body = resp.json()

    assert body["handled_event_type"] == "RESULT_ADDED"
    assert len(body["created_notifications"]) == 1

    notif = body["created_notifications"][0]
    assert notif["recipient_email"] == "patient@example.com"
    assert notif["status"] == "SENT"
    assert len(notifications_store) == 1


def test_list_notifications_by_email():
    """
    GET /api/v1/notifications?email=... возвращает только уведомления для этого адреса.
    """
    # одно уведомление для patient@example.com
    event1 = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-7",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    notification_service.handle_analysis_event(event1)

    # другое уведомление для другого пользователя
    event2 = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-8",
        patient_email="other@example.com",
        doctor_email=None,
        patient_name="Другой",
    )
    notification_service.handle_analysis_event(event2)

    resp = client.get("/api/v1/notifications", params={"email": "patient@example.com"})
    assert resp.status_code == 200
    items = resp.json()

    assert len(items) == 1
    assert items[0]["recipient_email"] == "patient@example.com"


def test_read_notification_endpoint_changes_status():
    """
    POST /api/v1/notifications/{id}/read меняет статус на READ.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-9",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    created = notification_service.handle_analysis_event(event)
    notif = created[0]

    resp = client.post(f"/api/v1/notifications/{notif.id}/read")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "READ"
    assert notifications_store[notif.id].status == NotificationStatus.READ


def test_mark_as_important_endpoint_sets_flag():
    """
    POST /api/v1/notifications/{id}/important ставит is_important = true.
    """
    event = AnalysisResultEvent(
        event_type="RESULT_ADDED",
        analysis_id="a-10",
        patient_email="patient@example.com",
        doctor_email=None,
        patient_name="Пациент",
    )
    created = notification_service.handle_analysis_event(event)
    notif = created[0]

    resp = client.post(f"/api/v1/notifications/{notif.id}/important")
    assert resp.status_code == 200
    data = resp.json()

    assert data["is_important"] is True
    assert notifications_store[notif.id].is_important is True


def test_read_unknown_notification_returns_404():
    """
    Чтение несуществующего уведомления -> 404.
    """
    resp = client.post("/api/v1/notifications/unknown-id/read")
    assert resp.status_code == 404
