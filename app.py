import pytesseract
from utils import (
    detect_skills,
    get_skill_gap,
    calculate_skill_coverage,
    validate_resume_text,
    extract_resume_text,
    calculate_job_match_score,
    
)

import io
import html

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
import streamlit as st
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Database file
DB_NAME = "career_readiness.db"

# Create database and table
def initialize_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            analysis_date TEXT,
            total_skills INTEGER,
            detected_skills TEXT,
            file_hash TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


# Save resume analysis
def save_analysis(file_name, skills, file_hash):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO resume_analysis
        (file_name, analysis_date, total_skills,
         detected_skills, file_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (
        file_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        len(skills),
        ", ".join(skills),
        file_hash
    ))

    conn.commit()
    saved = cursor.rowcount > 0
    conn.close()

    return saved


# Initialize database
initialize_database()


st.set_page_config(
    page_title="AI Career Readiness System",
    page_icon="🎓",
    layout="wide"
)


# Technical skills
SKILLS = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "Power BI",
    "Excel",
    "Streamlit",
    "Git",
    "GitHub",
    "Data Analysis",
    "Flask",
    "Django",
    "FastAPI",
    "OpenCV",
    "Matplotlib",
    "Seaborn",
    "PyTorch",
    "Statistics",
    "Data Visualization",
    "REST API",
    "MongoDB",
    "MySQL"
]

# Job roles and required skills

JOB_ROLES = {

    "Python Developer": {
        "skills": [
            "Python", "SQL", "Git", "GitHub",
            "Flask", "Django", "REST API"
        ],
        "description": (
            "Python programming software development "
            "object oriented programming SQL database "
            "Flask Django REST API Git GitHub debugging"
        )
    },

    "Data Analyst": {
        "skills": [
            "Python", "SQL", "Pandas", "NumPy",
            "Power BI", "Excel", "Statistics",
            "Matplotlib", "Data Visualization"
        ],
        "description": (
            "Data analysis Python SQL Pandas NumPy "
            "Excel Power BI statistics data cleaning "
            "data visualization reporting Matplotlib"
        )
    },

    "Machine Learning Engineer": {
        "skills": [
            "Python", "Machine Learning", "Scikit-learn",
            "Pandas", "NumPy", "Statistics",
            "TensorFlow", "PyTorch"
        ],
        "description": (
            "Machine learning Python Scikit-learn "
            "TensorFlow PyTorch model training "
            "data preprocessing statistics "
            "Pandas NumPy prediction"
        )
    },

    "Web Developer": {
        "skills": [
            "HTML", "CSS", "JavaScript",
            "React", "REST API", "Git"
        ],
        "description": (
            "Web development frontend development "
            "HTML CSS JavaScript React responsive "
            "websites REST API Git"
        )
    },

    "AI / NLP Developer": {
        "skills": [
            "Python", "NLP", "Machine Learning",
            "Scikit-learn", "TensorFlow",
            "Deep Learning", "PyTorch"
        ],
        "description": (
            "Artificial intelligence Python NLP "
            "natural language processing machine learning "
            "deep learning TensorFlow PyTorch "
            "text processing language models"
        )
    },

    "Power BI Developer": {
        "skills": [
            "SQL", "Power BI", "Excel",
            "Data Analysis", "Data Visualization",
            "Statistics"
        ],
        "description": (
            "Power BI SQL Excel data analysis "
            "business intelligence dashboards "
            "DAX data visualization reporting "
            "statistics"
        )
    }
}

# Learning recommendations
LEARNING = {
    "Python": "Practice Python functions, OOP and projects.",
    "SQL": "Learn joins, subqueries and database management.",
    "Git": "Practice Git commands and version control.",
    "GitHub": "Upload projects and create a professional portfolio.",
    "Pandas": "Practice data cleaning and data manipulation.",
    "NumPy": "Learn arrays and numerical operations.",
    "Power BI": "Build interactive dashboards and reports.",
    "Excel": "Learn formulas, pivot tables and charts.",
    "Machine Learning": "Study regression, classification and model evaluation.",
    "Scikit-learn": "Practice building and evaluating ML models.",
    "TensorFlow": "Learn neural networks and deep learning.",
    "NLP": "Study text preprocessing and natural language processing.",
    "HTML": "Learn webpage structure.",
    "CSS": "Practice responsive webpage styling.",
    "JavaScript": "Learn programming for interactive websites.",
    "React": "Build components and frontend applications.",
    "Java": "Practice Java OOP and programming fundamentals.",
    "C++": "Learn OOP and data structures.",
    "Deep Learning": "Study neural networks and backpropagation.",
    "Streamlit": "Build interactive Python web applications.",
    "Data Analysis": "Practice exploratory data analysis and visualization.",
    "Flask" : "Learn routing, templates and building Python web applications.",
    "Django": "Learn Django models, views, templates and REST framework.",
    "FastAPI": "Practice building REST APIs using Python.",
    "OpenCV": "Learn image processing, object detection and computer vision.",
    "Matplotlib": "Practice creating charts and data visualizations.",
    "Seaborn": "Learn statistical data visualization using Python.",
    "PyTorch": "Practice building and training neural networks.",
    "Statistics": "Study probability, distributions and hypothesis testing.",
    "Data Visualization": "Learn how to present data using charts and dashboards.",
    "REST API": "Learn HTTP methods, API requests and JSON responses.",
    "MongoDB": "Learn NoSQL databases, collections and queries.",
    "MySQL": "Practice SQL queries, joins and database management."
}

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "detected_skills" not in st.session_state:
    st.session_state.detected_skills = []


# Professional application styling
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #102A43;
}

[data-testid="stSidebar"] label {
    color: white !important;
}

h1 {
    color: #173B65;
}
</style>
""", unsafe_allow_html=True)

st.title("AI-Powered Career Readiness System")

st.sidebar.markdown("""
<div style="text-align: center; padding: 15px 5px;">
    <h2 style="color: #FFFFFF; font-size: 25px;">
        CareerAI
    </h2>
    <p style="color: #D6E4F0; font-size: 13px;">
        Smart Career Analytics
    </p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Resume Analyzer",
        "Job Recommendations",
        "Skill Gap Analysis",
        "Analysis History"
    ]
)


# Dashboard
# Dashboard
def add_page_number(canvas, pdf):
    canvas.saveState()

    page_number = canvas.getPageNumber()

    canvas.setStrokeColor(colors.grey)
    canvas.line(50, 35, 562, 35)

    canvas.setFont("Helvetica", 9)

    canvas.drawString(
        50, 20,
        "AI Career Readiness System"
    )

    canvas.drawRightString(
        550, 20,
        f"Page {page_number}"
    )

    canvas.restoreState()

if menu == "Dashboard":

    st.header("Career Dashboard")

    st.markdown("""
    <div style="
        background: linear-gradient(120deg, #173B65, #2878B5);
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    ">
        <h2 style="color: white; margin-bottom: 8px;">
            Welcome to CareerAI!
        </h2>
        <p style="font-size: 15px; margin-bottom: 0;">
            Analyze your resume, discover suitable career opportunities,
            and identify the skills you need to grow.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dashboard styling
    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background-color: #F0F5FF;
            border: 1px solid #D6E4FF;
            padding: 20px;
            border-radius: 12px;
        }

        .skill-chip {
            display: inline-block;
            background-color: #E8F1FF;
            color: #174EA6;
            padding: 8px 14px;
            margin: 5px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # Dashboard metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Skills Found",
        len(st.session_state.detected_skills)
    )

    col2.metric(
        "Available Job Roles",
        len(JOB_ROLES)
    )

    col3.metric(
        "Resume Status",
        "Analyzed" if st.session_state.resume_text else "Pending"
    )

    st.divider()

    # Resume analysis status
    if st.session_state.resume_text:

        st.success("Resume analysis completed successfully!")

        st.subheader("Your Detected Technical Skills")

        skills = st.session_state.detected_skills or []

        if skills:

            # Display skills in rows of four
            for start in range(0, len(skills), 4):

                skill_columns = st.columns(4)

                for i, skill in enumerate(skills[start:start + 4]):

                    with skill_columns[i]:
                        st.markdown(
                            f'<div class="skill-chip">✓ {html.escape(skill)}</div>',
                            unsafe_allow_html=True
                        )

        else:
            st.info("No technical skills detected yet.")
            st.divider()

        st.subheader("Skills Analytics")
        st.caption("Overview of technical skills detected in your resume.")

        if skills:
            skills_data = pd.DataFrame({
                "Skill": skills,
                "Count": [1] * len(skills)
            })

            st.bar_chart(
                skills_data.set_index("Skill"),
                horizontal=True
            )
        else:
            st.info("Upload a resume with technical skills to view analytics.")

    else:

        st.info(
            "Welcome! Upload your resume in Resume Analyzer "
            "to view your career insights here."
        )
        st.divider()

    st.subheader("Your Next Steps")
    st.caption("Continue improving your career readiness with CareerAI.")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 💼")
            st.markdown("**Explore Job Roles**")
            st.write(
                "Discover career opportunities that match your skills."
            )

    with col2:
        with st.container(border=True):
            st.markdown("### 🎯")
            st.markdown("**Identify Skill Gaps**")
            st.write(
                "Find missing skills and understand what you need to learn."
            )

    with col3:
        with st.container(border=True):
            st.markdown("### 📄")
            st.markdown("**Generate Career Report**")
            st.write(
                "Generate a PDF report with your career analysis."
            )



# Resume Analyzer

elif menu == "Resume Analyzer":

    st.header("Resume Analyzer")

    st.markdown(
        "Upload your resume and let AI analyze your technical skills."
    )

    st.divider()

    # Resume upload
    st.subheader("Upload Your Resume")

    uploaded_file = st.file_uploader(
        "Choose your resume in PDF format",
        type=["pdf"],
        help="Upload a text-based or scanned PDF resume."
    )

    if uploaded_file is not None:

        st.info(
            f"Selected file: {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.2f} KB)"
        )

        try:

            resume_text = extract_resume_text(
                uploaded_file.getvalue()
            )

            if validate_resume_text(resume_text):

                detected_skills = detect_skills(
                    resume_text,
                    SKILLS
                )

                st.session_state.resume_text = resume_text
                st.session_state.detected_skills = detected_skills

                # Duplicate resume detection
                file_hash = hashlib.sha256(
                    uploaded_file.getvalue()
                ).hexdigest()

                saved = save_analysis(
                    uploaded_file.name,
                    detected_skills,
                    file_hash
                )

                st.divider()

                # Analysis status
                st.subheader("Analysis Results")

                if saved:
                    st.success(
                        "Resume analysis saved successfully!"
                    )
                else:
                    st.info(
                        "This resume analysis is already saved."
                    )

                st.success(
                    "Resume analyzed successfully!"
                )

                # Total skills metric
                st.metric(
                    "Total Technical Skills Found",
                    len(detected_skills)
                )

                st.divider()

                # Display detected skills
                st.subheader("Your Technical Skills")

                if detected_skills:

                    st.markdown(
                        "The following technical skills were detected "
                        "in your resume:"
                    )

                    cols = st.columns(3)

                    for index, skill in enumerate(detected_skills):

                        with cols[index % 3]:
                            st.success(f"✓ {skill}")

                else:

                    st.warning(
                        "No technical skills detected in this resume."
                    )

                st.divider()

                # Resume text preview
                with st.expander("View Extracted Resume Text"):

                    st.text_area(
                        "Resume Content",
                        resume_text,
                        height=300
                    )

            else:

                st.warning(
                    "No readable text found in this PDF. "
                    "Please upload another resume."
                )

        except Exception as e:

            st.error(f"Error reading PDF: {e}")

    else:

        st.info(
            "Please upload a PDF resume to begin your career analysis."
        )





# Job Recommendations


elif menu == "Job Recommendations":

    st.header("AI Job Recommendations")

    resume_text = st.session_state.resume_text
    detected_skills = st.session_state.detected_skills

    if not resume_text:

        st.warning("Please upload your resume first.")

    else:

        # Get available career roles
        roles = list(JOB_ROLES.keys())

        descriptions = [
            JOB_ROLES[role]["description"]
            for role in roles
        ]

        # Convert resume and job descriptions into TF-IDF vectors
        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        matrix = vectorizer.fit_transform(
            [resume_text] + descriptions
        )

        # Calculate text similarity
        scores = cosine_similarity(
            matrix[0:1],
            matrix[1:]
        )[0]

        results = []

        # Calculate combined matching score
        for i, role in enumerate(roles):

            required_skills = JOB_ROLES[role]["skills"]

            # TF-IDF similarity percentage
            text_score = scores[i] * 100

            # Skill coverage percentage
            skill_score = calculate_skill_coverage(
                detected_skills,
                required_skills
            )

            # Combined score: 60% text + 40% skills
            final_score =calculate_job_match_score(
               text_score,
               skill_score
            )

            results.append(
                (
                    role,
                    final_score,
                    text_score,
                    skill_score
                )
            )

        # Sort by highest combined score
        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        
        
        # Professional recommendation display
        st.subheader("Top 3 Recommended Career Roles")

        st.caption(
            "Career paths ranked according to your resume content "
            "and technical skill coverage."
        )

        for index, (role, final_score, text_score, skill_score) in enumerate(results[:3]):

            required_skills = JOB_ROLES[role]["skills"]

            matched_skills, missing_skills = get_skill_gap(
                detected_skills,
                required_skills
            )

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(f"🏆 {index + 1}. {role}")
                    st.caption("Recommended career role")

                with col2:
                    st.metric(
                        "Overall Match",
                        f"{final_score:.2f}%"
                    )

                st.progress(
                    min(float(final_score) / 100, 1.0)
                )

                score1, score2 = st.columns(2)

                with score1:
                    st.metric(
                        "Text Similarity",
                        f"{text_score:.2f}%"
                    )

                with score2:
                    st.metric(
                        "Skill Coverage",
                        f"{skill_score:.2f}%"
                    )

                st.divider()

                skill1, skill2 = st.columns(2)

                with skill1:
                    st.markdown("**✅ Skills You Have**")

                    if matched_skills:
                        for skill in matched_skills:
                            st.write(f"✓ {skill}")
                    else:
                        st.info("No matching skills found.")

                with skill2:
                    st.markdown("**📚 Skills to Improve**")

                    if missing_skills:
                        for skill in missing_skills:
                            st.write(f"• {skill}")
                    else:
                        st.success("All listed skills matched!")

        st.caption(
            "Combined score = 60% text similarity + 40% skill coverage. "
            "This is a project-specific matching score, not a hiring "
            "probability or guarantee of employment."
        )








# Skill Gap Analysis
elif menu == "Skill Gap Analysis":

    st.header("Resume Score & Skill Gap Analysis")

    detected_skills = st.session_state.detected_skills

    if not st.session_state.resume_text:

        st.warning("Please upload your resume first.")

    else:

        selected_role = st.selectbox(
            "Select your target career role",
            list(JOB_ROLES.keys())
        )

        required_skills = JOB_ROLES[selected_role]["skills"]
        matched_skills, missing_skills = get_skill_gap(
    detected_skills,
    required_skills
)

        coverage = round(
            len(matched_skills) / len(required_skills) * 100
        )

        
        # Professional Skill Coverage
        st.subheader("Your Career Readiness Overview")

        st.caption(
            f"Your current skills compared with the requirements "
            f"for {selected_role}."
        )

        # Coverage summary
        st.markdown("### Skill Coverage Score")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Overall Coverage",
                f"{coverage}%"
            )

        with col2:
            st.metric(
                "Skills Matched",
                len(matched_skills)
            )

        with col3:
            st.metric(
                "Skills Missing",
                len(missing_skills)
            )

        st.progress(coverage / 100)

        st.divider()

        # Matched and missing skills
        st.subheader("Technical Skills Assessment")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("### ✅ Skills You Have")

                if matched_skills:
                    for skill in matched_skills:
                        st.success(skill)
                else:
                    st.info("No matching skills found.")

        with col2:
            with st.container(border=True):
                st.markdown("### 📚 Skills to Improve")

                if missing_skills:
                    for skill in missing_skills:
                        st.warning(skill)
                else:
                    st.success("All listed skills are covered!")

        st.divider()

        # Skill coverage chart
        st.subheader("Skill Coverage Visualization")

        chart_data = pd.DataFrame({
            "Category": ["Matched Skills", "Missing Skills"],
            "Count": [
                len(matched_skills),
                len(missing_skills)
            ]
        })

        st.bar_chart(
            chart_data.set_index("Category")
        )

        st.divider()

        # Learning recommendations
        st.subheader("Personalized Learning Roadmap")

        if missing_skills:

            for skill in missing_skills:

                recommendation = LEARNING.get(
                    skill,
                    "Practice this skill through practical projects."
                )

                with st.container(border=True):
                    st.markdown(f"**📘 {skill}**")
                    st.write(recommendation)

        else:
            st.success(
                "Excellent! All skills in this role's checklist are covered."
            )

        st.caption(
            "This score measures coverage of the selected role's "
            "listed skills. It is not a guarantee of employment."
        )


        st.divider()

        st.subheader("Download Career Analysis Report")

        if st.button("Generate PDF Report"):

            buffer = io.BytesIO()

            pdf = SimpleDocTemplate(
                buffer,
                pagesize=letter
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
    name="CustomTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=20,
    textColor=colors.HexColor("#1F4E79"),
    alignment=1,
    spaceAfter=12
)
            section_style = ParagraphStyle(
    name="SectionHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    textColor=colors.HexColor("#1F4E79"),
    spaceBefore=12,
    spaceAfter=8
)
            content = []

            # Report title
            content.append(
    Paragraph(
        "AI Career Readiness Analysis Report",
        title_style
    )
)

            content.append(Spacer(1, 10))

            # Report generation date
            report_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")

            content.append(
           Paragraph(
        f"Report Generated: {report_date}",
        styles["Normal"]
    )
)

            content.append(Spacer(1, 20))
            # Candidate analysis details
    

            content.append(Spacer(1, 15))

           
           
                        # Candidate summary
            content.append(
                Paragraph(
                    "Candidate Summary",
                    section_style
                )
            )

            summary_data = [
                ["Metric", "Value"],
                ["Total Skills Detected", str(len(detected_skills))],
                ["Required Skills", str(len(required_skills))],
                ["Matched Skills", str(len(matched_skills))],
                ["Missing Skills", str(len(missing_skills))]
            ]

            summary_table = Table(summary_data)

            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("PADDING", (0, 0), (-1, -1), 8)
            ]))

            content.append(summary_table)
            content.append(Spacer(1, 15))

  

            # Matched skills
            content.append(
                Paragraph("Skills You Have", section_style)
            )

            for skill in matched_skills:
                content.append(
                    Paragraph(
                        html.escape(skill),
                        styles["Normal"]
                    )
                )

            content.append(Spacer(1, 15))

            # Missing skills
            content.append(
                Paragraph("Skills You Need to Learn", section_style)
            )

            if missing_skills:

                for skill in missing_skills:
                    content.append(
                        Paragraph(
                            html.escape(skill),
                            styles["Normal"]
                        )
                    )

            else:
                content.append(
                    Paragraph(
                        "No missing skills from this role's checklist.",
                        styles["Normal"]
                    )
                )

            content.append(Spacer(1, 15))

            # Learning recommendations
            content.append(
                Paragraph(
                    "Learning Recommendations",
                    section_style
                )
            )

            for skill in missing_skills:

                recommendation = LEARNING.get(
                    skill,
                    "Practice this skill through practical projects."
                )

                content.append(
                    Paragraph(
                        f"<b>{html.escape(skill)}:</b> "
                        f"{html.escape(recommendation)}",
                        styles["Normal"]
                    )
                )

                content.append(Spacer(1, 6))

            content.append(Spacer(1, 20))

            content.append(
                Paragraph(
                    "Note: This report measures skill coverage "
                    "against the selected role's checklist. "
                    "It does not guarantee employment.",
                    styles["Italic"]
                )
            )

            # Create PDF
            pdf.build(
    content,
    onFirstPage=add_page_number,
    onLaterPages=add_page_number
)

            buffer.seek(0)

            st.download_button(
                label="Download PDF Report",
                data=buffer.getvalue(),
                file_name="Career_Analysis_Report.pdf",
                mime="application/pdf"
            )



# Analysis History
elif menu == "Analysis History":

    st.header("Resume Analysis History")
    st.caption("View and track your previously analyzed resumes.")
    st.divider()

    conn = sqlite3.connect(DB_NAME)

    history = pd.read_sql_query(
        """
        SELECT
            id AS ID,
            file_name AS Resume,
            analysis_date AS Date,
            total_skills AS 'Total Skills',
            detected_skills AS 'Detected Skills'
        FROM resume_analysis
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    if not history.empty:
        st.success("Previous analysis records found!")

    st.metric(
        "Total Saved Analyses",
        len(history)
    )

    st.subheader("Saved Resume Records")

    st.dataframe(
        history,
        width="stretch",
        hide_index=True
    )

    csv_data = history.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download History as CSV",
        data=csv_data,
        file_name="Resume_Analysis_History.csv",
        mime="text/csv"
    )

else:

    st.info("No resume analysis records available yet.")
    st.markdown("""
<hr>

<div style="text-align: center; padding: 15px; color: #808495;">

    <h4 style="color: #173B65;">
        CareerAI – Smart Career Analytics
    </h4>

    <p>
        AI-Powered Career Readiness System
    </p>

    <p style="font-size: 12px;">
        This application provides career guidance based on resume analysis.
        It does not guarantee employment or job selection.
    </p>

    <p style="font-size: 12px;">
        © 2026 CareerAI. MCA Internship Project.
    </p>

</div>
""", unsafe_allow_html=True)


        