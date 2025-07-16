import pdfplumber

def extract_text_from_pdf(pdf_path):
    """
    PDF 파일에서 모든 페이지의 텍스트를 추출하여 하나의 문자열로 반환합니다.
    표/이미지 등은 제외하고 텍스트만 추출합니다.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text 