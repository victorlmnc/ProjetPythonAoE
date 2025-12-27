import pdfplumber

def extract_text(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += f"--- Page {i+1} ---\n{text}\n\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Extracted text to {output_path}")

if __name__ == "__main__":
    extract_text("ProjetPython-1-20.pdf", "requirements_text.txt")
