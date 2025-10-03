import os
import shutil

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

from lunbi.config import DATA_PATH, CHROMA_PATH

load_dotenv()


def load_documents() -> list[Document]:
    loader = DirectoryLoader(str(DATA_PATH), glob="*.md")
    docs = loader.load()
    print(f"Loaded {len(docs)} docs from {DATA_PATH}.")
    return docs


def split_text(docs: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Split {len(docs)} docs into {len(chunks)} chunks.")
    return chunks


def save_to_chroma(chunks: list[Document]) -> None:
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=str(CHROMA_PATH)
    )
    print(f"Saved {len(chunks)} to {CHROMA_PATH}.")


def main() -> None:
    docs = load_documents()
    chunks = split_text(docs)
    save_to_chroma(chunks)


if __name__ == "__main__":
    main()
