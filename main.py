from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pdf2image import convert_from_bytes
import pytesseract
from docx import Document
from PIL import Image
import uuid
import os

app = FastAPI()

@app.post("/convert/")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    # Generate temporary filenames
    pdf_bytes = await file.read()
    output_filename = f"{uuid.uuid4().hex}.docx"

    # Step 1: Convert PDF to images
    try:
        images = convert_from_bytes(pdf_bytes)
    except Exception as e:
        return {"error": f"PDF to image conversion failed: {e}"}

    # Step 2: OCR each image
    text_list = []
    for img in images:
        text = pytesseract.image_to_string(img)
        text_list.append(text)

    # Step 3: Save text to .docx
    doc = Document()
    for paragraph in text_list:
        cleaned = ''.join(c for c in paragraph if c.isprintable())
        doc.add_paragraph(cleaned)
    doc.save(output_filename)

    # Step 4: Return the file
    response = FileResponse(
        path=output_filename,
        filename="converted.docx",
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

    return response
