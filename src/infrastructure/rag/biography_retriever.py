

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.infrastructure.config.settings import Settings


class BiographyRetrieverFactory:
    def __init__(self, *, settings: Settings, embeddings) -> None:
        self._settings = settings
        self._embeddings = embeddings

    def create_tool(self):
        vector_store = Chroma(
            collection_name=self._settings.vector_collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(self._settings.vector_store_dir),
        )
        self._seed_if_needed(vector_store, self._settings.biography_pdf_path)
        retriever = vector_store.as_retriever(search_kwargs={"k": self._settings.retriever_k})
        return create_retriever_tool(
            retriever=retriever,
            name="retrieve_vladimir_information_tool",
            description="Retrieves information about Vladimir.",
        )

    def _seed_if_needed(self, vector_store: Chroma, pdf_path: Path) -> None:
        if vector_store._collection.count() > 0:
            return
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Biography PDF not found at '{pdf_path}'. Set BIOGRAPHY_PDF_PATH or provide the file."
            )
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        vector_store.add_documents(splitter.split_documents(docs))
