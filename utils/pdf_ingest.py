import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDF 파일에서 모든 페이지의 텍스트를 추출합니다.
    텍스트 추출 실패 시 OCR로 이미지에서 텍스트 추출을 시도합니다.
    Args:
        pdf_path (str): PDF 파일 경로
    Returns:
        str: 추출된 텍스트 또는 오류 메시지
    """
    text: str = ""
    # 1차: pdfplumber로 텍스트 추출
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception as e:
        # pdfplumber 실패 시 OCR로 넘어감
        pass
    # 2차: OCR로 이미지에서 텍스트 추출
    try:
        images = convert_from_path(pdf_path)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img, lang='kor+eng+jpn') + "\n"
        if ocr_text.strip():
            return "[OCR 추출 결과]\n" + ocr_text
        else:
            return "오류: PDF에서 텍스트를 추출할 수 없습니다. (텍스트/이미지 모두 실패)"
    except Exception as e:
        return f"오류: PDF에서 텍스트를 추출할 수 없습니다. (OCR 실패: {e})" 