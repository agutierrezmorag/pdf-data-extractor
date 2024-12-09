import os
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
    texts = [read_pdf(pdf) for pdf in pdf_files]
    prompts = [prompt_template.invoke({"data": text}) for text in texts]

    # Batch process all prompts
    results = llm.with_structured_output(schema=Invoice).batch(prompts)
    return results


def save_results(results, pdf_files, output_dir="output"):
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save each result as JSON
    for pdf_file, result in zip(pdf_files, results):
        json_path = output_path / f"{pdf_file.stem}.json"
        print(f"Saving to {json_path}")
        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def main():
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            ("human", "{data}"),
        ]
    )

    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    docs_dir = Path("docs")
    pdf_files = list(docs_dir.glob("*.pdf"))

    print(f"Processing {len(pdf_files)} PDF files...")
    results = process_pdfs(pdf_files, llm, prompt_template)

    # Save results to JSON files
    save_results(results, pdf_files)


if __name__ == "__main__":
    main()
