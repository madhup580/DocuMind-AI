import re


def split_text(text, chunk_size=500, chunk_overlap=100):
    """
    Split document text into chunks while preserving page numbers.
    """

    if not text:
        return []

    chunks = []

    # Find page markers such as [PAGE 1], [PAGE 2], etc.
    page_pattern = r"\[PAGE\s+(\d+)\]\s*(.*?)(?=\[PAGE\s+\d+\]|$)"

    pages = re.findall(
        page_pattern,
        text,
        flags=re.DOTALL
    )

    # If page markers were not found, fall back to normal chunking.
    if not pages:
        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "text": chunk,
                    "page": 1
                })

            start += chunk_size - chunk_overlap

        return chunks

    # Create chunks for each page
    for page_number, page_text in pages:

        page_text = page_text.strip()

        if not page_text:
            continue

        start = 0

        while start < len(page_text):

            end = start + chunk_size

            chunk_text = page_text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "text": chunk_text,
                    "page": int(page_number)
                })

            start += chunk_size - chunk_overlap

    return chunks