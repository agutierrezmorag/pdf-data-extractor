import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pypdf import PdfReader

from doc_template import Invoice

load_dotenv()


def read_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def process_pdfs(pdf_files: List[Path], llm, prompt_template):
    # Read all PDFs and create prompts
    print("Reading PDFs...")
    texts = [read_pdf(pdf) for pdf in pdf_files]
    print("Formatting prompts...")
    prompts = [prompt_template.invoke({"data": text}) for text in texts]

    # Batch process all prompts
    print("Batch processing prompts...")
    results = llm.with_structured_output(schema=Invoice).batch(prompts)
    return results


def init_db(db_path="invoices.db"):
    """Initialize SQLite database with required tables"""
    with closing(sqlite3.connect(db_path)) as conn:
        with closing(conn.cursor()) as cur:
            # Create tables for main invoice data with address fields
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_number TEXT PRIMARY KEY,
                    date TEXT,
                    due_date TEXT,
                    currency TEXT,
                    customer_id TEXT,
                    po_number TEXT,
                    sales_order TEXT,
                    sap_number TEXT,
                    container TEXT,
                    incoterms TEXT,
                    messers TEXT,
                    origin TEXT,
                    payment_terms TEXT,
                    total_cases INTEGER,
                    total_quantity TEXT,
                    total_value REAL,
                    pdf_filename TEXT,
                    -- Company address fields
                    company_street TEXT,
                    company_city TEXT,
                    company_state TEXT,
                    company_zip_code TEXT,
                    company_country TEXT,
                    company_phone TEXT,
                    -- Customer address fields
                    customer_street TEXT,
                    customer_city TEXT,
                    customer_state TEXT,
                    customer_zip_code TEXT, 
                    customer_country TEXT,
                    customer_phone TEXT
                )
            """)

            # Create table for line items
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT,
                    cases INTEGER,
                    code TEXT,
                    goods_descriptions TEXT,
                    quantity TEXT,
                    unit_value REAL,
                    FOREIGN KEY (invoice_number) REFERENCES invoices(invoice_number)
                )
            """)
        conn.commit()


def save_to_db(result, pdf_file, db_path="output/invoices.db"):
    """Save invoice data to SQLite database"""
    with closing(sqlite3.connect(db_path)) as conn:
        with closing(conn.cursor()) as cur:
            # Convert Pydantic model to dict
            data = json.loads(result.model_dump_json())

            # Insert main invoice data including addresses
            invoice_values = {
                "invoice_number": data.get("invoice_number"),
                "date": data.get("date"),
                "due_date": data.get("due_date"),
                "currency": data.get("currency"),
                "customer_id": data.get("customer_id"),
                "po_number": data.get("po_number"),
                "sales_order": data.get("sales_order"),
                "sap_number": data.get("sap_number"),
                "container": data.get("container"),
                "incoterms": data.get("incoterms"),
                "messers": data.get("messers"),
                "origin": data.get("origin"),
                "payment_terms": data.get("payment_terms"),
                "total_cases": data.get("total_cases"),
                "total_quantity": data.get("total_quantity"),
                "total_value": data.get("total_value"),
                "pdf_filename": pdf_file.name,
                # Company address
                "company_street": data.get("address", {}).get("street"),
                "company_city": data.get("address", {}).get("city"),
                "company_state": data.get("address", {}).get("state"),
                "company_zip_code": data.get("address", {}).get("zip_code"),
                "company_country": data.get("address", {}).get("country"),
                "company_phone": data.get("address", {}).get("phone"),
                # Customer address
                "customer_street": data.get("customer_address", {}).get("street"),
                "customer_city": data.get("customer_address", {}).get("city"),
                "customer_state": data.get("customer_address", {}).get("state"),
                "customer_zip_code": data.get("customer_address", {}).get("zip_code"),
                "customer_country": data.get("customer_address", {}).get("country"),
                "customer_phone": data.get("customer_address", {}).get("phone"),
            }

            cur.execute(
                """
                INSERT OR REPLACE INTO invoices 
                VALUES (:invoice_number, :date, :due_date, :currency, :customer_id,
                       :po_number, :sales_order, :sap_number, :container, :incoterms,
                       :messers, :origin, :payment_terms, :total_cases, :total_quantity,
                       :total_value, :pdf_filename,
                       :company_street, :company_city, :company_state, :company_zip_code,
                       :company_country, :company_phone,
                       :customer_street, :customer_city, :customer_state, :customer_zip_code,
                       :customer_country, :customer_phone)
            """,
                invoice_values,
            )

            # Insert items (unchanged)
            if data.get("items"):
                for item in data["items"]:
                    cur.execute(
                        """
                        INSERT INTO items (invoice_number, cases, code, goods_descriptions,
                                        quantity, unit_value)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            data["invoice_number"],
                            item.get("cases"),
                            item.get("code"),
                            item.get("goods_descriptions"),
                            item.get("quantity"),
                            item.get("unit_value"),
                        ),
                    )

        conn.commit()


def save_results(results, pdf_files, output_dir="output"):
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Initialize database
    db_path = output_path / "invoices.db"
    init_db(db_path)

    # Save each result as JSON and to database
    for pdf_file, result in zip(pdf_files, results):
        # Save to JSON
        json_path = output_path / f"{pdf_file.stem}.json"
        print(f"Saving to {json_path}")
        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

        # Save to SQLite
        print(f"Saving to database: {pdf_file.name}")
        save_to_db(result, pdf_file, db_path)


def main():
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
                "Write every value as-is, do NOT change the format.",
            ),
            ("human", "{data}"),
        ]
    )

    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )

    docs_dir = Path("docs")
    pdf_files = list(docs_dir.glob("*.pdf"))

    print(f"Processing {len(pdf_files)} PDF files...")
    results = process_pdfs(pdf_files, llm, prompt_template)

    # Save results to JSON files and database
    save_results(results, pdf_files)


if __name__ == "__main__":
    main()
