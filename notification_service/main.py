from __future__ import annotations

import json
import os
import threading
import time
import uuid
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Literal

import stomp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ====================== КОНФИГ ======================

# Параметры очереди ActiveMQ / RabbitMQ (STOMP)
MQ_HOST = os.getenv("MQ_HOST", "localhost")
MQ_PORT = int(os.getenv("MQ_PORT", "61613"))
# Очередь, куда сервис анализа шлёт события про результаты
MQ_QUEUE = os.getenv("MQ_QUEUE", "/queue/analysis.result.events")
MQ_USER = os.getenv("MQ_USER", "")
MQ_PASSWORD = os.getenv("MQ_PASSWORD", "")

# Настройки «отправки» писем
EMAIL_FROM = os.getenv("EMAIL_FROM", "no-reply@example.com")
EMAIL_PRINT_ONLY = os.getenv("EMAIL_PRINT_ONLY", "true").lower() == "true"

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "notifications.log"


# ====================== ДОМЕН ======================

class RecipientType(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"


class NotificationStatus(str, Enum):
    CREATED = "CREATED"
    SENT = "SENT"
    READ = "READ"


class Notification(BaseModel):
    """
    Агрегат «Уведомление» из правой части схемы.
    """
    id: str
    analysis_id: Optional[str] = None
    recipient_type: RecipientType
    recipient_email: str
    subject: str
    body: str
    is_important: bool = False
    status: NotificationStatus = NotificationStatus.CREATED


# События, которые приходят из контекста «Результат анализа» через MQ.
class AnalysisResultEvent(BaseModel):
    """
    event_type:
      - RESULT_ADDED        -> «Результат анализа добавлен»
      - RESULT_UPDATED      -> «Результат анализа обновлён»
      - RESULT_CONFIRMED    -> «Результат подтверждён»
      - RESULT_VIEWED       -> «Результат просмотрен»
    """
    event_type: Literal["RESULT_ADDED", "RESULT_UPDATED",
                        "RESULT_CONFIRMED", "RESULT_VIEWED"]
    analysis_id: str
    patient_email: Optional[str] = None
    doctor_email: Optional[str] = None
    patient_name: Optional[str] = None


# DTO для REST-эндпоинта теста (имитация события из очереди)
class TestEventRequest(AnalysisResultEvent):
    pass


# In-memory хранилище (для учебы)
notifications_store: Dict[str, Notification] = {}


# ====================== EMAIL-СЕРВИС (заглушка) ======================

def send_email(to_email: str, subject: str, body: str) -> None:
    """
    По диаграмме: «Отправить уведомление пациенту/врачу».
    Здесь мы просто печатаем письмо и пишем в файл.
    """
    message = f"FROM: {EMAIL_FROM}\nTO: {to_email}\nSUBJECT: {subject}\n\n{body}"

    print("=== EMAIL START ===")
    print(message)
    print("=== EMAIL END ===")

    LOG_FILE.parent.mkdir(exist_ok=True, parents=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write("\n\n" + "=" * 40 + "\n")
        f.write(message)

    if EMAIL_PRINT_ONLY:
        return

    # сюда можно добавить реальную отправку через smtplib.SMTP(...)


# ====================== ДОМЕННЫЙ СЕРВИС УВЕДОМЛЕНИЙ ======================

class NotificationService:
    """
    Именно тут реализуются команды из схемы:
    - Создать и отправить уведомление пациенту
    - Отправить уведомление врачу
    - Прочитать уведомление
    - Отметить уведомление как важное
    - Отметить уведомление как прочитанное
    """

    # --- команды, реагирующие на события из анализа ---

    def handle_analysis_event(self, event: AnalysisResultEvent) -> List[Notification]:
        """
        Маппинг событий из «Результата анализа» на команды уведомлений.
        """
        created: List[Notification] = []

        if event.event_type in ("RESULT_ADDED", "RESULT_UPDATED"):
            # Создать и отправить уведомление пациенту
            if event.patient_email:
                created.append(self._create_and_send_to_patient(event))

        if event.event_type == "RESULT_CONFIRMED":
            # Отправить уведомление врачу
            if event.doctor_email:
                created.append(self._send_to_doctor(event))

        if event.event_type == "RESULT_VIEWED":
            # Результат просмотрен -> отметить уведомления как прочитанные
            if event.patient_email:
                self.mark_as_read_by_analysis(event.analysis_id, event.patient_email)

        return created

    def _create_and_send_to_patient(self, event: AnalysisResultEvent) -> Notification:
        notif_id = str(uuid.uuid4())
        patient_name = event.patient_name or "Пациент"

        subject = "Результаты анализа"
        body_lines = [
            f"Здравствуйте, {patient_name}!",
            "",
            "Результат вашего анализа обновлён.",
            "Проверьте, пожалуйста, детали в личном кабинете.",
        ]
        body = "\n".join(body_lines)

        notif = Notification(
            id=notif_id,
            analysis_id=event.analysis_id,
            recipient_type=RecipientType.PATIENT,
            recipient_email=event.patient_email,  # type: ignore[arg-type]
            subject=subject,
            body=body,
        )

        notifications_store[notif.id] = notif
        send_email(notif.recipient_email, notif.subject, notif.body)
        notif.status = NotificationStatus.SENT
        notifications_store[notif.id] = notif

        print(f"[NotificationService] Created & sent to patient: {notif.id}")
        return notif

    def _send_to_doctor(self, event: AnalysisResultEvent) -> Notification:
        notif_id = str(uuid.uuid4())

        subject = "Результат анализа пациента подтверждён"
        body_lines = [
            "Здравствуйте!",
            "",
            "Результат анализа пациента был подтверждён.",
            "Проверьте, пожалуйста, информацию в системе.",
        ]
        body = "\n".join(body_lines)

        notif = Notification(
            id=notif_id,
            analysis_id=event.analysis_id,
            recipient_type=RecipientType.DOCTOR,
            recipient_email=event.doctor_email,  # type: ignore[arg-type]
            subject=subject,
            body=body,
        )

        notifications_store[notif.id] = notif
        send_email(notif.recipient_email, notif.subject, notif.body)
        notif.status = NotificationStatus.SENT
        notifications_store[notif.id] = notif

        print(f"[NotificationService] Sent to doctor: {notif.id}")
        return notif

    def mark_as_read_by_analysis(self, analysis_id: str, email: str) -> None:
        """
        Используется для события RESULT_VIEWED:
        все уведомления по этому анализу для данного получателя
        помечаем как прочитанные.
        """
        for notif in notifications_store.values():
            if (
                notif.analysis_id == analysis_id
                and notif.recipient_email == email
                and notif.status != NotificationStatus.READ
            ):
                notif.status = NotificationStatus.READ
                notifications_store[notif.id] = notif
                print(f"[NotificationService] Notification {notif.id} auto-marked READ")

    # --- команды, приходящие по REST от пользователей ---

    def mark_read(self, notification_id: str) -> Notification:
        notif = notifications_store.get(notification_id)
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")

        notif.status = NotificationStatus.READ
        notifications_store[notif.id] = notif
        print(f"[NotificationService] Notification {notif.id} marked READ (REST)")
        return notif

    def mark_important(self, notification_id: str) -> Notification:
        notif = notifications_store.get(notification_id)
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")

        notif.is_important = True
        notifications_store[notif.id] = notif
        print(f"[NotificationService] Notification {notif.id} marked IMPORTANT")
        return notif

    def list_for_email(self, email: str) -> List[Notification]:
        return [n for n in notifications_store.values() if n.recipient_email == email]


notification_service = NotificationService()


# ====================== MQ LISTENER ======================

class AnalysisEventListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print(f"[MQ] Error: {frame.body}")

    def on_message(self, frame):
        print(f"[MQ] Message: {frame.body}")
        try:
            data = json.loads(frame.body)
            event = AnalysisResultEvent(**data)
        except Exception as e:  # noqa: BLE001
            print(f"[MQ] Failed to parse message: {e}")
            return

        notification_service.handle_analysis_event(event)


class MQClient:
    def __init__(self):
        self.conn: Optional[stomp.Connection] = None
        self.thread: Optional[threading.Thread] = None
        self._stop_flag = False

    def start(self):
        def _run():
            while not self._stop_flag:
                try:
                    print(f"[MQ] Connecting to {MQ_HOST}:{MQ_PORT}, queue={MQ_QUEUE}...")
                    conn = stomp.Connection([(MQ_HOST, MQ_PORT)])
                    conn.set_listener("analysis-listener", AnalysisEventListener())
                    conn.connect(login=MQ_USER, passcode=MQ_PASSWORD, wait=True)
                    conn.subscribe(destination=MQ_QUEUE, id="1", ack="auto")
                    self.conn = conn
                    print("[MQ] Connected and subscribed.")
                    while not self._stop_flag and conn.is_connected():
                        time.sleep(1)
                except Exception as e:  # noqa: BLE001
                    print(f"[MQ] Connection error: {e}")
                    time.sleep(5)

        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_flag = True
        if self.conn and self.conn.is_connected():
            self.conn.disconnect()


mq_client = MQClient()


# ====================== FASTAPI + SWAGGER ======================

app = FastAPI(
    title="Notification Service",
    description=(
        "Контекст управления уведомлениями.\n\n"
        "• По событиям из очереди (результат анализа добавлен/обновлён/подтверждён/"
        "просмотрен) создаёт и отправляет уведомления пациенту или врачу.\n"
        "• Позволяет читать уведомления и отмечать их как важные/прочитанные."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
def on_startup():
    print("[App] Starting MQ client...")
    mq_client.start()


@app.on_event("shutdown")
def on_shutdown():
    print("[App] Stopping MQ client...")
    mq_client.stop()


# -------- системный health-check --------

@app.get("/health", tags=["system"], summary="Состояние сервиса")
def health_check():
    return {"status": "ok"}


# -------- REST-команды из схемы --------

@app.get(
    "/api/v1/notifications",
    tags=["notifications"],
    summary="Список уведомлений по email",
)
def list_notifications(email: str):
    """
    Получить список уведомлений для конкретного получателя.
    """
    return notification_service.list_for_email(email)


@app.post(
    "/api/v1/notifications/{notification_id}/read",
    tags=["notifications"],
    summary="Прочитать уведомление",
)
def read_notification(notification_id: str):
    """
    Команда «Прочитать уведомление».
    Помечает уведомление как прочитанное.
    """
    return notification_service.mark_read(notification_id)


@app.post(
    "/api/v1/notifications/{notification_id}/mark-as-read",
    tags=["notifications"],
    summary="Отметить уведомление как прочитанное",
)
def mark_as_read(notification_id: str):
    """
    Команда «Отметить уведомление как прочитанное».
    Логически то же самое, что и 'Прочитать уведомление',
    вынесено отдельным эндпоинтом под диаграмму.
    """
    return notification_service.mark_read(notification_id)


@app.post(
    "/api/v1/notifications/{notification_id}/important",
    tags=["notifications"],
    summary="Отметить уведомление как важное",
)
def mark_notification_important(notification_id: str):
    """
    Команда «Отметить уведомление как важное».
    """
    return notification_service.mark_important(notification_id)


# -------- тестовый эндпоинт: имитируем событие из очереди --------

@app.post(
    "/api/v1/notifications/test-event",
    tags=["notifications"],
    summary="Протестировать обработку события анализа (без MQ)",
)
def test_event(req: TestEventRequest):
    """
    Этот метод полностью имитирует получение сообщения из очереди.
    Удобно для проверки через Swagger, когда ActiveMQ ещё не поднят.
    """
    created = notification_service.handle_analysis_event(req)
    return {
        "handled_event_type": req.event_type,
        "created_notifications": created,
    }
