
from utils import extract_resume_text
from io import BytesIO
import pymupdf

from PIL import Image, ImageDraw, ImageFont


def test_extract_empty_pdf():

    # Create an empty PDF
    pdf = pymupdf.open()
    pdf.new_page()

    pdf_bytes = pdf.tobytes()
    pdf.close()

    # Extract text
    result = extract_resume_text(pdf_bytes)

    # Check that result is empty
    assert result.strip() == ""


def test_extract_image_pdf():

    # Create an image containing text
    image = Image.new("RGB", (1600, 400), "white")
    draw = ImageDraw.Draw(image)

    # Load font
    font = ImageFont.truetype(
        r"C:\Windows\Fonts\arial.ttf",
        90
    )

    # Write text on image
    draw.text(
        (60, 120),
        "Python SQL Java",
        fill="black",
        font=font
    )

    # Convert image into PDF
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")

    pdf = pymupdf.open()
    page = pdf.new_page(width=1600, height=400)

    page.insert_image(
        page.rect,
        stream=image_buffer.getvalue()
    )

    pdf_bytes = pdf.tobytes()
    pdf.close()

    # Extract text using OCR
    result = extract_resume_text(pdf_bytes)

    # Check extracted words
    assert "Python" in result
    assert "SQL" in result
    assert "Java" in result

    
   