
# AI-Powered Career Readiness & Job Matching System

## 1. Project Introduction

The AI-Powered Career Readiness & Job Matching System is a Python-based application developed using Streamlit.

The system analyzes a candidate's resume, identifies technical skills, compares them with the required skills for different job roles, and provides job recommendations.

It also identifies missing skills and provides learning recommendations to help candidates improve their career readiness.


## 2. Project Objectives

- To extract text from PDF resumes.
- To identify technical skills from candidate resumes.
- To analyze candidate skills against different job roles.
- To recommend suitable job roles.
- To calculate skill coverage and identify missing skills.
- To provide learning recommendations for missing skills.
- To generate downloadable career analysis reports in PDF format.
- To maintain candidate analysis history using SQLite.


## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application interface |
| PyMuPDF | Extract text from PDF resumes |
| Tesseract OCR | Extract text from scanned resumes |
| Pillow | Image processing |
| Scikit-learn | TF-IDF and cosine similarity |
| Pandas | Data handling |
| SQLite | Store analysis history |
| ReportLab | Generate PDF reports |
| Pytest | Software testing |


## 4. Project Features

1. **Resume Upload:** Upload PDF resumes for analysis.
2. **Text Extraction:** Extract resume text using PyMuPDF and Tesseract OCR.
3. **Skill Detection:** Identify technical skills from resumes.
4. **Job Recommendations:** Recommend suitable job roles using TF-IDF and cosine similarity.
5. **Skill Gap Analysis:** Compare detected skills with required job skills.
6. **Skill Coverage:** Calculate the percentage of matched skills.
7. **Learning Recommendations:** Suggest topics to learn missing skills.
8. **PDF Report:** Generate downloadable career analysis reports.
9. **Analysis History:** Store previous analysis records using SQLite.
10. **Duplicate Detection:** Identify duplicate resumes using SHA-256 hashing.


## 5. Installation and Setup

### Prerequisites

- Python 3.13
- Visual Studio Code
- Tesseract OCR

### Step 1: Clone or Download the Project

Download the project and open its folder in VS Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Required Libraries

```bash
pip install streamlit pymupdf pytesseract pillow scikit-learn pandas reportlab pytest
```

### Step 5: Run the Application

```bash
streamlit run app.py
```


## 6. Project Structure

```text
MCA_AI_Project/
│
├── app.py
├── utils.py
├── tests/
│   ├── test_utils.py
│   └── test_resume_extraction.py
│
├── README.md
├── career_readiness.db
└── venv/
```

## 7. How to Use the Application

1. Run the Streamlit application.
2. Open the application in your web browser.
3. Navigate to the Resume Analyzer section.
4. Upload your PDF resume.
5. Allow the system to extract and analyze resume information.
6. View detected skills and job recommendations.
7. Open Skill Gap Analysis to check matched and missing skills.
8. Review the learning recommendations.
9. Generate and download the career analysis PDF report.
10. Visit Analysis History to view previous analysis records.

## 8. Testing

The project uses Pytest for automated testing.

Run the following command:

```bash
python -m pytest -v
```

The test suite covers:

- Resume text extraction.
- Image-based PDF extraction using OCR.
- Technical skill detection.
- Skill coverage calculation.
- Skill gap analysis.
- Resume text validation.
- Job matching score calculation.
- Edge cases and special-character skills.

Latest recorded test result: 12 tests passed.

## 9. Technologies and Algorithms

The project uses the following techniques:

- Regular Expressions for skill detection.
- TF-IDF Vectorization for text similarity.
- Cosine Similarity for job matching.
- Weighted scoring using text similarity and skill coverage.
- SHA-256 hashing for duplicate resume detection.
- OCR for extracting text from scanned PDF pages.

## 10. Future Enhancements

- Add more job roles and technical skills.
- Improve resume analysis accuracy.
- Add more detailed career recommendations.
- Support additional resume formats.
- Improve the user interface.
- Expand automated testing.

## 11. Disclaimer

This application is developed for educational and career guidance purposes.

The job matching score represents similarity between resume information and selected job-role requirements. It is not a hiring probability or guarantee of employment.

## 12. Author

**Project:** AI-Powered Career Readiness & Job Matching System

**Course:** Master of Computer Applications (MCA)

**Project Type:** MCA Internship Project
```
