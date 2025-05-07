import os
import re
import nltk
from nltk.tokenize import sent_tokenize
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import difflib
from pdf2image import convert_from_path
import pytesseract

# download tokenizer
nltk.download('punkt')

def extract_ocr_text_from_pdf(pdf_path, dpi=300):
    """
    Extract full text from a PDF using OCR.
    """
    pages = convert_from_path(pdf_path, dpi=dpi)
    text = ""
    for page in pages:
        page_text = pytesseract.image_to_string(page)
        text += page_text + "\n"
    return text

def smart_split_into_paragraphs(text):
    """
    Split text into paragraphs based on double newlines to preserve whitespace.
    """
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def get_html_diff(exp_text, ren_text, context=False, numlines=0):
    """
    Generate an HTML diff table comparing two text blocks.
    """
    hd = difflib.HtmlDiff(wrapcolumn=80)
    return hd.make_table(exp_text.splitlines(),
                         ren_text.splitlines(),
                         fromdesc="Expiring", todesc="Renewal",
                         context=context, numlines=numlines)

def wrap_in_div(html_content, title):
    """Wrap given HTML content in a div with a header title."""
    return f"<h3>{title}</h3><div>{html_content}</div><hr>"

def print_text_diff(exp_text, ren_text):
    """
    Generate a unified diff for two text blocks.
    """
    diff = difflib.unified_diff(
        exp_text.splitlines(),
        ren_text.splitlines(),
        fromdesc='Expiring',
        todesc='Renewal',
        lineterm=''
    )
    return "\n".join(diff)

def clean_text_for_comparison(text):
    """
    Remove dates and policy numbers from the text to avoid false change detections.
    """
    # Remove dates like "April 1, 2024"
    text = re.sub(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                  r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|'
                  r'Dec(?:ember)?)\s+\d{1,2},\s+\d{4}', '', text, flags=re.IGNORECASE)
    
    # Remove dates like "04/01/2024" or "4/1/24"
    text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '', text)
    
    # Remove dates like "2024-04-01"
    text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '', text)
    
    return text.strip()

def main(expiring_pdf, renewal_pdf, threshold=0.99):
    html_parts = []
    html_parts.append("<html><head><meta charset='UTF-8'><title>Policy Diff - Entire Policy</title>")
    html_parts.append("""
    <style>
    body { font-family: Calibri, sans-serif; }
    table.diff {font-family:Courier; border:medium;}
    .diff_header {background-color:#e0e0e0}
    .diff_next {background-color:#c0c0c0}
    .diff_add {background-color:#aaffaa}
    .diff_chg {background-color:#ffff77}
    .diff_sub {background-color:#ffaaaa}
    pre { background-color: #f4f4f4; padding: 10px; }
    </style>
    """)
    html_parts.append("</head><body>")
    html_parts.append("<h1>Expiring vs. Renewal Policy Comparison Report</h1>")

    # Step 1: Extract full OCR text from both PDFs
    expiring_text = extract_ocr_text_from_pdf(expiring_pdf)
    renewal_text = extract_ocr_text_from_pdf(renewal_pdf)

    # Step 2: Split full OCR text into paragraphs
    expiring_paragraphs = smart_split_into_paragraphs(expiring_text)
    renewal_paragraphs = smart_split_into_paragraphs(renewal_text)
    
    html_parts.append(f"<p>Number of paragraphs in Expiring Policy: {len(expiring_paragraphs)}</p>")
    html_parts.append(f"<p>Number of paragraphs in Renewal Policy: {len(renewal_paragraphs)}</p>")
    
    # Step 3: Compare paragraphs using sentence embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    exp_embeddings = model.encode(expiring_paragraphs)
    ren_embeddings = model.encode(renewal_paragraphs)
    similarity_matrix = cosine_similarity(exp_embeddings, ren_embeddings)
    
    detected_change = False
    for i, exp_para in enumerate(expiring_paragraphs):
        j = np.argmax(similarity_matrix[i])
        max_sim = similarity_matrix[i][j]
        ren_para = renewal_paragraphs[j]
        
        if exp_para != ren_para:
            detected_change = True
            diff_html = get_html_diff(exp_para, ren_para, context=False)
            html_parts.append(wrap_in_div(diff_html, "Please review change in policy"))
            html_parts.append("<hr>")
    
    html_parts.append("</body></html>")
    output_html = "\n".join(html_parts)
    
    with open("diff_output.html", "w", encoding="utf-8") as f:
        f.write(output_html)
    print("HTML diff report written to diff_output.html")

    return detected_change

if __name__ == "__main__":
    expiring_pdf = "/Users/kristinlussi/Documents/GitHub/DATA698/Slip-Examples/ABC COMPANY @ 04-01-2024.pdf"
    renewal_pdf = "/Users/kristinlussi/Documents/GitHub/DATA698/Slip-Examples/ABC COMPANY @ 04-01-2025.pdf"
    main(expiring_pdf, renewal_pdf, threshold=0.95)