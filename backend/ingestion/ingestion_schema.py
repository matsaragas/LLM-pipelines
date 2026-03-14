from pydantic import Field, BaseModel
from typing import Dict, Any, Set, List
from enum import Enum
from llama_index.core.schema import BaseNode, Optional



class IngestionResult(BaseModel):
    total_nodes: int = Field(0, descruption="Total Nodes Ingested")
    nodes: Optional[List[Dict[str, Any]]] = Field(default_factory=list, descruption="Details of Nodes Ingested")
    total_documents: int = Field(0, descruption="Total Documents Ingested")
    documents: Optional[List[str]] = Field(default_factory=list, descruption="Details of Documents Ingested")
