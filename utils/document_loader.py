from pypdf import PdfReader


def load_pdf(file_path):
    """Extract text from a PDF file."""
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def get_page_count(file_path):
    """Return the number of pages in a PDF."""
    reader = PdfReader(file_path)

    return len(reader.pages)