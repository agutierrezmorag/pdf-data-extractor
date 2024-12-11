import os

import pandas as pd
import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from streamlit_pdf_viewer import pdf_viewer

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

    st.toast("Reading PDFs...")
    texts = [read_pdf(pdf) for pdf in pdf_files]
    st.toast("Formatting texts...")
    prompts = [prompt_template.invoke({"data": text}) for text in texts]

    # Batch process all prompts
    st.toast("Batch pdfs...")
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

    if uploaded_files:
        with st.sidebar:
            st.divider()
            for i, uploaded_file in enumerate(uploaded_files):
                # Add unique key for each pdf viewer instance
                pdf_viewer(
                    uploaded_file.getvalue(), key=f"pdf_viewer_{i}_{uploaded_file.name}"
                )

    if uploaded_files and process_button:
        transcriptions = process_pdfs(uploaded_files)
        dfs = []

        for i, transcription in enumerate(transcriptions):
            df = pd.json_normalize(
                transcription.model_dump(),
                record_path="items",
                meta=[
                    col for col in transcription.model_dump().keys() if col != "items"
                ],
            )
            df["invoice_id"] = i + 1  # Keep for internal tracking
            dfs.append(df)

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            # Hide invoice_id by excluding it from display columns
            display_cols = [col for col in combined_df.columns if col != "invoice_id"]
            st.dataframe(combined_df[display_cols], hide_index=True)

            # Display raw JSON data in expanders
            st.divider()
            for transcription in transcriptions:
                with st.expander(
                    f"Raw Data: Invoice {transcription.invoice_number} - {transcription.messers}"
                ):
                    st.json(transcription.model_dump())


if __name__ == "__main__":
    main()
