from enum import Enum
from pathlib import Path
from uuid import uuid4
from typing import Optional
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document as DocxDocument


# ==== Настройки ====

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

FONTS_DIR = BASE_DIR / "fonts"
FONT_FILE = FONTS_DIR / "DejaVuSans.ttf"  # положи сюда шрифт с кириллицей
FONT_NAME = "DejaVuSans"

if FONT_FILE.exists():
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_FILE)))
else:
    print("WARNING: font file not found, using default PDF font (кириллица может ломаться)")
    FONT_NAME = "Helvetica"


# ==== Модели ====

class DocumentFormat(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"


class GenerateDocumentRequest(BaseModel):
    template_code: str
    format: DocumentFormat
    data: dict


class GenerateDocumentResponse(BaseModel):
    document_id: str
    file_name: str
    format: DocumentFormat


# ==== Шаблоны текста ====

def build_analysis_text(data: dict) -> Optional[str]:
    """
    Собираем человекочитаемый текст для шаблона ANALYSIS_RESULT.
    Никаких id и служебного JSON — только то, что нужно пользователю.
    Ожидаем, что в data есть ключ 'analysis'.
    """
    analysis = data.get("analysis")
    if not isinstance(analysis, dict):
        return None

    patient_name = analysis.get("patient_name", "—")
    hemoglobin = analysis.get("hemoglobin")
    conclusion = analysis.get("conclusion", "—")
    date = analysis.get("date") or analysis.get("created_at")

    # дополнительные параметры, кроме основных
    exclude_keys = {"patient_name", "conclusion", "id", "date", "created_at"}
    extra_params = {
        k: v for k, v in analysis.items()
        if k not in exclude_keys
    }

    lines = [
        "РЕЗУЛЬТАТ ЛАБОРАТОРНОГО АНАЛИЗА",
        "",
        f"Пациент: {patient_name}",
    ]

    if date:
        lines.append(f"Дата анализа: {date}")

    lines.append("")
    lines.append("Основные показатели:")

    if hemoglobin is not None:
        lines.append(f"  • Гемоглобин: {hemoglobin}")

    if extra_params:
        lines.append("")
        lines.append("Дополнительные параметры:")
        for k, v in extra_params.items():
            lines.append(f"  • {k}: {v}")

    lines.append("")
    lines.append("Заключение:")
    lines.append(f"  {conclusion}")

    return "\n".join(lines)


def build_text_from_data(template_code: str, data: dict) -> str:
    """
    Выбираем шаблон в зависимости от template_code.
    Для ANALYSIS_RESULT делаем красивый отчёт без служебного JSON.
    Для остальных шаблонов по-прежнему выводим красивый JSON.
    """
    if template_code == "ANALYSIS_RESULT":
        analysis_text = build_analysis_text(data)
        if analysis_text:
            return analysis_text

    # дефолтный вариант – просто красивый JSON (для других шаблонов)
    lines = [f"Шаблон: {template_code}", ""]
    lines.append("Данные объекта (JSON):")
    pretty = json.dumps(data, ensure_ascii=False, indent=2)
    lines.append(pretty)
    return "\n".join(lines)


# ==== Генерация файлов ====

def generate_pdf(path: Path, text: str) -> None:
    """
    Генерация PDF: заголовок крупно по центру, остальное — обычный текст.
    """
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    lines = text.splitlines()
    if not lines:
        lines = ["Документ"]

    header = lines[0]
    body_lines = lines[1:]

    title_font_size = 18
    text_font_size = 12

    # заголовок по центру
    c.setFont(FONT_NAME, title_font_size)
    header_width = pdfmetrics.stringWidth(header, FONT_NAME, title_font_size)
    x_header = (width - header_width) / 2
    y = height - 60
    c.drawString(x_header, y, header)

    # отступ вниз
    y -= 30

    # основной текст
    c.setFont(FONT_NAME, text_font_size)
    line_height = 16
    x_margin = 50

    for line in body_lines:
        if not line:
            y -= line_height
        else:
            c.drawString(x_margin, y, line)
            y -= line_height

        if y < 50:
            c.showPage()
            c.setFont(FONT_NAME, text_font_size)
            y = height - 50

    c.save()


def generate_docx(path: Path, text: str) -> None:
    doc = DocxDocument()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(path)


def find_document_file(doc_id: str) -> Optional[Path]:
    pdf_path = STORAGE_DIR / f"{doc_id}.pdf"
    docx_path = STORAGE_DIR / f"{doc_id}.docx"

    if pdf_path.exists():
        return pdf_path
    if docx_path.exists():
        return docx_path
    return None


# ==== Приложение FastAPI + Swagger ====

app = FastAPI(
    title="Document Generation Service",
    description=(
        "Микросервис для генерации документов (PDF/DOCX) на основе "
        "результатов анализа. Предоставляет REST API для создания "
        "документа и выгрузки его содержимого."
    ),
    version="1.0.0",
    docs_url="/docs",            # Swagger UI
    redoc_url="/redoc",          # ReDoc
    openapi_url="/openapi.json", # JSON-схема OpenAPI
)


@app.post(
    "/api/v1/documents",
    response_model=GenerateDocumentResponse,
    tags=["documents"],
    summary="Сгенерировать документ",
    response_description="Информация о сгенерированном документе",
)
def generate_document(request: GenerateDocumentRequest):
    """
    Создаёт новый документ на основе переданных данных.

    - **template_code**: код шаблона (например, `ANALYSIS_RESULT`)
    - **format**: формат документа (`PDF` или `DOCX`)
    - **data**: произвольный JSON с данными, которые будут использованы в шаблоне

    Возвращает идентификатор документа и имя файла.
    """
    document_id = str(uuid4())
    text = build_text_from_data(request.template_code, request.data)

    if request.format == DocumentFormat.PDF:
        file_name = f"{document_id}.pdf"
        file_path = STORAGE_DIR / file_name
        generate_pdf(file_path, text)

    elif request.format == DocumentFormat.DOCX:
        file_name = f"{document_id}.docx"
        file_path = STORAGE_DIR / file_name
        generate_docx(file_path, text)

    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

    return GenerateDocumentResponse(
        document_id=document_id,
        file_name=file_name,
        format=request.format,
    )


@app.get(
    "/api/v1/documents/{document_id}/content",
    tags=["documents"],
    summary="Выгрузить документ",
    response_description="Бинарное содержимое документа",
)
def download_document(document_id: str):
    """
    Отдаёт содержимое ранее сгенерированного документа по его идентификатору.

    - **document_id**: идентификатор документа, полученный при создании

    Возвращает файл в формате PDF или DOCX.
    """
    file_path = find_document_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    if file_path.suffix.lower() == ".pdf":
        media_type = "application/pdf"
    else:
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name,
    )