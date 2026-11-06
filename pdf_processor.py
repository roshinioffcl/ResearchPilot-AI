
import pymupdf


def extract_pages(pdf_bytes, filename):

    # Validate empty files
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    # Open the PDF
    try:
        doc = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )
    except Exception as error:
        raise ValueError(
            f"Could not open {filename}. It may be corrupted or invalid."
        ) from error

    # Check password protection
    if doc.needs_pass:
        doc.close()
        raise ValueError(f"{filename} is password-protected.")

    pages = []

    try:
        for page_number, page in enumerate(doc, start=1):

            text = page.get_text()

            page_data = {
                "document": filename,
                "page": page_number,
                "text": text
            }

            pages.append(page_data)

    finally:
        doc.close()

    return pages
