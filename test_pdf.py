import pdfplumber

pdf_path = "invoices/invoice_2.pdf"

with pdfplumber.open(pdf_path) as pdf:

    print("Total Pages:", len(pdf.pages))

    for i, page in enumerate(pdf.pages, start=1):

        print(f"\n===== PAGE {i} =====\n")

        text = page.extract_text()

        print(text)