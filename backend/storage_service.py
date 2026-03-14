from llama_index.vector_stores.opensearch import (
    OpensearchVectorStore,
    OpensearchVectorClient,
)
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.storage.index_store.postgres import PostgresIndexStore
from llama_index.storage.docstore.postgres import PostgresDocumentStore

from llama_index.storage.kvstore.postgres import PostgresKVStore
from llama_index.core.storage.kvstore.types import DEFAULT_COLLECTION, BaseKVStore
from db_setup import get_db_url


class StorageService:
    def __init__(self, store_config):

        self.pg_doc_kv_store = self._set_kv_store(
            table_name=f"experiment_bbc_ds",
            use_jsonb=True,
            perform_setup=True,
        )

        self.pg_index_kv_store = self._set_kv_store(
            table_name=f"experiment_bbc_is",
            use_jsonb=True,
            perform_setup=True,
        )
        store_config_bbc = store_config['contexts']['bbc_docs']['store_configs']

        client = OpensearchVectorClient(endpoint="http://localhost:9200",
                                        index="gpt-index-demo",
                                        embedding_field="embedding",
                                        text_field="content",
                                        dim=1536,
                                        **store_config_bbc
                                        )

        vector_store = OpensearchVectorStore(client)

        self.storage_context = (
            StorageContext.from_defaults(
                docstore=PostgresDocumentStore(self.pg_doc_kv_store),
                index_store=PostgresIndexStore(self.pg_index_kv_store),
                vector_store=vector_store
            )
        )

    @staticmethod
    def _set_kv_store(table_name: str,
                      perform_setup: bool = True,
                      debug: bool = False,
                      use_jsonb: bool = True
                      ) -> BaseKVStore:
        url = get_db_url()
        return PostgresKVStore.from_params(
            database="vectortutorial",
            host=url.host,
            password=url.password,
            port=url.port,
            user=url.username,
            table_name=table_name,
            perform_setup=perform_setup,
            debug=debug,
            use_jsonb=use_jsonb
        )