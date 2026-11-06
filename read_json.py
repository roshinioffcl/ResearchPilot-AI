
import json

# Open the JSON file
with open("data/processed/extracted_pages.json", "r", encoding="utf-8") as file:

    pages = json.load(file)

# Display information
print("Total pages loaded:", len(pages))

for item in pages:
    print("\nDocument:", item["document"])
    print("Page:", item["page"])
    print("Text length:", len(item["text"]))
