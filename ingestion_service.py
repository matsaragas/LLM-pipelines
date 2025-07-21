from llama_index.core.ingestion import IngestionPipeline
from typing import Set, Dict, Any, List, Optional
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import MarkdownNodeParser
from storage_service import StorageService
from ingestion.ingestion_schema import IngestionResult

from config import Settings
import logging

api_key = Settings.api_key

logging = logging.getLogger(__name__)


class IngestionService:
    def __init__(
            self,
            storage_service: StorageService,
            transformation_bbc: List[Dict[str, Any]]
    ) -> None:
        self.transformation_bbc = transformation_bbc
        self.storage_service = storage_service

    def _build_pipeline(self) -> IngestionPipeline:
        """
        Builds an ingestion pipeline with transformations and embeddings.
        """
        transformations = [
            MarkdownNodeParser(**t.get('args', {}))
            for t in self.transformation_bbc
        ]

        vector_store = self.storage_service.storage_context.vector_store
        docstore = self.storage_service.storage_context.docstore

        embed_model = OpenAIEmbedding(
            max_retries=50,
            embed_batch_size=50,
            model="text-embedding-ada-002",
            api_key=api_key,
        )
        transformations.append(embed_model)

        return IngestionPipeline(
            transformations=transformations,
            vector_store=vector_store,
            docstore=docstore,
            disable_cache=True,
        )

    def run_ingestion(self, documents: List[Document]) -> IngestionResult:
        """
        Runs ingestion for the given list of documents.
        """
        try:
            pipeline = self._build_pipeline()
            nodes = pipeline.run(documents=documents)
            ingested_docs = list({node.ref_doc_id for node in nodes})

            return IngestionResult(
                total_nodes=len(nodes),
                total_documents=len(ingested_docs),
                documents=ingested_docs
            )
        except Exception as e:
            logging.exception("Error occurred during ingestion.")
            raise

    def run_ingestion_batch(
            self,
            documents: List[Document],
            start_batch: int,
            end_batch: int
    ) -> Optional[IngestionResult]:
        """
        Runs ingestion for a specific batch of documents.
        """
        logging.info(f"Processing batch range {start_batch}:{end_batch}")
        try:
            result = self.run_ingestion(documents)
            logging.info(f"Completed range {start_batch}:{end_batch}")
            return result
        except Exception:
            logging.exception(f"Exception while processing range {start_batch}:{end_batch}")
            return None

    def ingest(
            self,
            documents: List[Document],
            batch_size: int = 2,
            batch_process: bool = False
    ) -> IngestionResult:
        """
        Ingests documents, optionally in batches.
        """
        final_result = IngestionResult()

        if batch_process:
            for i in range(0, len(documents), batch_size):
                batch_result = self.run_ingestion_batch(
                    documents[i:i + batch_size],
                    i,
                    min(i + batch_size, len(documents))
                )

                if batch_result:
                    final_result.total_nodes += batch_result.total_nodes
                    final_result.total_documents += batch_result.total_documents
                    final_result.documents.extend(batch_result.documents)

            return final_result

        return self.run_ingestion(documents)