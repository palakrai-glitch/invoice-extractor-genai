import pdfplumber
import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv

# ==========================
# Load Environment Variables
# ==========================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-3.1-flash-lite")

# ==========================
# PDF Text Extraction
# ==========================

def extract_text_from_pdf(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# ==========================
# Text Cleaning
# ==========================

def clean_text(text):

    lines = text.split("\n")

    cleaned = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned.append(line)

    return "\n".join(cleaned)

# ==========================
# Prompt Creation
# ==========================

def create_prompt(invoice_text):

    return f"""
You are an expert invoice data extraction assistant.

Extract information from the invoice and return ONLY valid JSON.

Rules:
1. Return ONLY JSON.
2. Do not use markdown.
3. Do not use code fences.
4. If a field is missing, return null.
5. Never guess values.
6. Keep currency symbols if present.
7. line_items must be a list of objects:
   [{{"item":"...", "amount":"..."}}]

Required JSON structure:

{{
"invoice_number": null,
"invoice_date": null,
"due_date": null,
"billed_by": null,
"billed_to": null,
"line_items": [],
"subtotal": null,
"discount": null,
"tax_or_gst": null,
"total_amount": null,
"currency": null,
"payment_method": null,
"notes": null
}}

Invoice Text:

{invoice_text}
"""
# ==========================
# Gemini Extraction
# ==========================

def extract_invoice_data(text):

    prompt = create_prompt(text)

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return None

# ==========================
# Parse JSON
# ==========================

def parse_json(response_text):

    try:

        response_text = response_text.strip()

        response_text = response_text.replace( "```json",  "").replace("```", "").strip()
        
        return json.loads(response_text)

    except Exception as e:

        print("JSON Error:", e)

        print(response_text)

        return None

# ==========================
# Save JSON Output
# ==========================

def save_output(data, filename):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

# ==========================
# Process Invoice
# ==========================

def process_invoice(pdf_path, output_path):
    print(f"\nProcessing: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)

    cleaned_text = clean_text(raw_text)

    if not cleaned_text.strip():
        print(f"Text extraction failed: {pdf_path}")
        return

    response = extract_invoice_data(cleaned_text)
   

    if not response:
        print("No response received from Gemini")
        return

    
    invoice_data = parse_json(response)

    if invoice_data:

        save_output(invoice_data, output_path)

        print("\n===== OUTPUT =====")

        for key, value in invoice_data.items():

            print(f"{key}: {value}")

    print(f"Output saved to: {output_path}")
# ==========================
# Run All Invoices
# ==========================

if __name__ == "__main__":

    invoices = [
        "invoice_1.pdf",
        "invoice_2.pdf",
        "invoice_3.pdf"
    ]

    for i, invoice in enumerate(invoices, start=1):

        process_invoice(
            f"invoices/{invoice}",
            f"outputs/output_invoice_{i}.json"
        )

        print("Waiting 15 seconds...")
        time.sleep(15)