import requests
import streamlit as st
import os
from docx import Document
import pdfplumber
from openai import OpenAI
import requests

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found. Please add it in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

st.title("AI-Powered Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
job_title = st.text_input("Enter the job title you want to apply for:")
user_email = st.text_input("Enter your email to receive the analysis:")

if st.button("Analyze Resume"):

    if not uploaded_file:
        st.error("Please upload a resume file.")
    elif not job_title.strip():
        st.error("Please enter the job title.")
    elif not user_email.strip():
        st.error("Please enter your email.")
    else:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file.name)
        else:
            resume_text = extract_text_from_docx(uploaded_file.name)

        prompt = f"""
You are a professional resume analyzer. Analyze the following resume text and provide:

1. A professional summary.
2. Top skills.
3. Suitability for the role of "{job_title}".
4. Areas of improvement.

Resume text:
{resume_text}

Your analysis:
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5,
        )

        analysis = response.choices[0].message.content
        st.subheader("Resume Analysis")
        st.write(analysis)

