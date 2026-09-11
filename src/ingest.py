import os
import time

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai._common import GoogleGenerativeAIError
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

BATCH_SIZE = 5
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 20


def add_documents_with_retry(store, batch):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            store.add_documents(batch)
            return
        except GoogleGenerativeAIError as e:
            if "429" not in str(e):
                raise
            if attempt == MAX_RETRIES:
                raise
            print(f"  Cota excedida, tentando novamente em {RETRY_DELAY_SECONDS}s (tentativa {attempt}/{MAX_RETRIES})...")
            time.sleep(RETRY_DELAY_SECONDS)


def ingest_pdf():
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=GOOGLE_EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )

    store = PGVector(
        embeddings=embeddings,
        connection=DATABASE_URL,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        use_jsonb=True,
    )
    store.delete_collection()
    store.create_collection()

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        print(f"Enviando lote {i // BATCH_SIZE + 1}/{-(-len(chunks) // BATCH_SIZE)} ({len(batch)} chunks)...")
        add_documents_with_retry(store, batch)

    print(f"Ingestão concluída: {len(chunks)} chunks gravados na coleção '{PG_VECTOR_COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest_pdf()
