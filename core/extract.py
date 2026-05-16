from pypdf import PdfReader

def extract_text(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        content = page.extract_text()

        if content:
            text += content

    return text

