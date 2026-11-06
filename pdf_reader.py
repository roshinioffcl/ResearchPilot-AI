
import pymupdf
import json
from pathlib import Path

# Find all PDF files
pdf_files = Path("data/documents").glob("*.pdf")

# Store all extracted pages
all_pages = []

# Process each PDF
for pdf_path in pdf_files:

    print(f"\nProcessing: {pdf_path.name}")

    doc = pymupdf.open(pdf_path)

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text()

        if not text.strip():
            print(f"Warning: No extractable text on page {page_number}")

        page_data = {
            "document": pdf_path.name,
            "page": page_number,
            "text": text
        }

        all_pages.append(page_data)

    doc.close()

# Save extracted data as JSON
output_path = Path("data/processed/extracted_pages.json")

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(all_pages, file, ensure_ascii=False, indent=4)

print("\nTotal pages processed:", len(all_pages))
print("JSON saved successfully:", output_path)
