import re
import pymupdf
import pytesseract
import io
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def detect_skills(resume_text, skill_list):
    detected = []

    for skill in skill_list:
        pattern = r'(?<![A-Za-z0-9])' + re.escape(skill) + r'(?![A-Za-z0-9])'

        if re.search(pattern, resume_text, re.IGNORECASE):
            detected.append(skill)

    return detected


def calculate_skill_coverage(detected_skills, required_skills):

    if not required_skills:
        return 0

    matched = {
        skill.lower() for skill in detected_skills
    }

    count = sum(
        1 for skill in required_skills
        if skill.lower() in matched
    )

    return round(
        count / len(required_skills) * 100
    )


def get_skill_gap(detected_skills, required_skills):

    matched_set = {
        skill.lower() for skill in detected_skills
    }

    matched = [
        skill for skill in required_skills
        if skill.lower() in matched_set
    ]

    missing = [
        skill for skill in required_skills
        if skill.lower() not in matched_set
    ]

    return matched, missing

def validate_resume_text(resume_text):

    if not resume_text:
        return False

    if not resume_text.strip():
        return False

    return True
def extract_resume_text(pdf_bytes):

    pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    resume_text = ""

    for page in pdf:

        text = page.get_text()

        if text.strip():
            resume_text += text

        else:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

            image = Image.open(
                io.BytesIO(pix.tobytes("png"))
            )

            text = pytesseract.image_to_string(image)

            resume_text += text

    pdf.close()

    return resume_text
def calculate_job_match_score(text_score, skill_score):

    final_score = (
        text_score * 0.60
        + skill_score * 0.40
    )

    return round(final_score, 2)