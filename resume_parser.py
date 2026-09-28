from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_text_from_docx(file_path):
    text = ""

    document = Document(file_path)

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_resume_text(file_path):

    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)

    else:
        raise ValueError("Only PDF and DOCX files are supported.")


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    file_path = input("Enter resume file path: ")

    resume_text = extract_resume_text(file_path)

    print("\n========== RESUME TEXT ==========\n")
    print(resume_text)

    print("\n=================================")
    print("Resume text extraction completed.")