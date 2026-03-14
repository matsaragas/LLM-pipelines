import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter

from storage_service import StorageService
from config import Settings

logger = logging.getLogger(__name__)

# Pydantic schemas for the API and LLM Structured Output
class FactCheck(BaseModel):
    theme_type: str = Field(description="The theme of the retrieved story")
    detail_response: str = Field(description="Provide statistics and numbers")
    short_response: str = Field(description="Provide important members of the identified story and describe what role they play")

class QueryRequest(BaseModel):
    query_str: str = Field(..., description="The query to execute against the index")
    theme: Optional[str] = Field(None, description="Filter results by theme (e.g., 'Politics', 'Sport')")
    country: Optional[str] = Field(None, description="Filter results by country (e.g., 'UK', 'US')")

class NodeResponse(BaseModel):
    node_id: str
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

class QueryResponse(BaseModel):
    response: str
    source_nodes: List[NodeResponse]

class QueryService:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
        self.api_key = Settings.api_key
        
        logger.info("Initializing LLM and Embedding models for querying.")
        self.embed_model = OpenAIEmbedding(
            max_retries=50,
            embed_batch_size=50,
            model="text-embedding-ada-002",
            api_key=self.api_key,
        )
        
        self.llm = OpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0,
            max_tokens=None,
            max_retries=2,
        )
        
        # We need the vector store to create the index for querying
        vector_store = self.storage_service.storage_context.vector_store
        
        # Initialize VectorStoreIndex
        # Pass the docstore explicitly if needed, but it should be resolvable 
        # from the global context or we can use from_vector_store
        logger.info("Creating VectorStoreIndex from vector store.")
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=self.embed_model
        )

    def _build_filters(self, request: QueryRequest) -> Optional[MetadataFilters]:
        filter_list = []
        if request.country:
            filter_list.append(ExactMatchFilter(key="country", value=request.country))
            
        # Specific formatting per notebook example
        if request.theme:
             filter_list.append(ExactMatchFilter(key="term", value=f'{{"metadata.theme.keyword": "{request.theme}"}}'))
        
        if not filter_list:
            return None
            
        return MetadataFilters(filters=filter_list)

    def query(self, request: QueryRequest) -> QueryResponse:
        """Executes a standard query returning unstructured text and sources."""
        logger.info(f"Executing standard query: '{request.query_str}'")
        filters = self._build_filters(request)
        
        query_engine = self.index.as_query_engine(
            llm=self.llm,
            similarity_top_k=3,
            filters=filters
        )
        
        response = query_engine.query(request.query_str)
        
        # Extract source nodes
        source_nodes = []
        for node_with_score in response.source_nodes:
             source_nodes.append(NodeResponse(
                 node_id=node_with_score.node.node_id,
                 text=node_with_score.node.text[:200] + "...", # truncate for brevity in payload
                 metadata=node_with_score.node.metadata,
                 score=node_with_score.score
             ))
             
        return QueryResponse(
            response=str(response),
            source_nodes=source_nodes
        )

    def query_structured(self, request: QueryRequest) -> FactCheck:
        """Executes a query returning a highly structured FactCheck object."""
        logger.info(f"Executing structured query: '{request.query_str}'")
        filters = self._build_filters(request)
        
        # Create a structured LLM
        sllm = self.llm.as_structured_llm(output_cls=FactCheck)
        
        query_engine = self.index.as_query_engine(
             llm=sllm, 
             similarity_top_k=2,
             filters=filters
        )
        
        response = query_engine.query(request.query_str)
        
        # The response.response object is directly the FactCheck Pydantic instance
        return response.response
