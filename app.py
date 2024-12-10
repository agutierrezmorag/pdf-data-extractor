import os

import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from doc_template import Invoice

load_dotenv()

LLM = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0,
)


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def process_pdfs(pdf_files) -> list[Invoice]:
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value."
                "Write every value as-is, do NOT change the format.",
            ),
            ("human", "{data}"),
        ]
    )

    print("Reading PDFs...")
    texts = [read_pdf(pdf) for pdf in pdf_files]
    print("Formatting prompts...")
    prompts = [prompt_template.invoke({"data": text}) for text in texts]

    # Batch process all prompts
    print("Batch processing prompts...")
    results = LLM.with_structured_output(schema=Invoice).batch(prompts)
    return results


def main():
    st.set_page_config(page_title="Invoice Parser", layout="wide")

    with st.sidebar:
        uploaded_files = st.file_uploader(
            "Upload PDF file",
            type=["pdf"],
            accept_multiple_files=True,
        )
        process_button = st.button(
            "Process PDFs",
            disabled=not uploaded_files,
            use_container_width=True,
            type="primary",
        )

    if uploaded_files and process_button:
        transcriptions = process_pdfs(uploaded_files)
        for transcription in transcriptions:
            with st.expander(
                f"ID {transcription.invoice_number} ({transcription.messers})"
            ):
                st.json(transcription.model_dump())


if __name__ == "__main__":
    main()
