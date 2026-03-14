from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from storage_service import StorageService
from ingestion_service import IngestionService
from query_service import QueryService, QueryRequest, QueryResponse, FactCheck
from ingestion.ingestion_config import transformation_bbc
from data_processing import load_schema, load_feed, generate_documents

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Ingestion API")

# Global services (initialized on startup)
storage_service = None
ingestion_service = None
query_service = None

@app.on_event("startup")
async def startup_event():
    global storage_service, ingestion_service, query_service
    logger.info("Starting up Ingestion API...")
    try:
        # Load configuration for storage and ingestion
        store_config = load_schema("data/store_config.yaml")
        
        # Initialize Services
        storage_service = StorageService(store_config)
        ingestion_service = IngestionService(storage_service, transformation_bbc)
        query_service = QueryService(storage_service)
        
        logger.info("Storage, Ingestion, and Query services initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize services during startup: {e}")
        # In a real production app, we might want to exit here if services are critical
        # raise e

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services_initialized": all([storage_service, ingestion_service, query_service])
    }

@app.post("/ingest")
async def run_ingestion(source: str = "bbc"):
    """
    Endpoint to trigger the data ingestion pipeline for a specific source.
    Currently only 'bbc' is supported.
    """
    logger.info(f"Received ingestion request for source: {source}")
    
    if storage_service is None or ingestion_service is None:
        logger.error("Services not initialized.")
        raise HTTPException(status_code=503, detail="Services are not initialized correctly.")

    try:
        if source != "bbc":
            logger.warning(f"Unsupported source requested: {source}")
            raise HTTPException(status_code=400, detail="Only 'bbc' source is currently supported.")
        
        # 1. Load data and schema
        # These paths are currently hardcoded based on the existing project structure
        logger.info("Loading raw data and schema...")
        raw_data = load_feed("data/news_feed.json")
        schema = load_schema("data/config.yaml")
        
        # 2. Generate LlamaIndex Documents
        logger.info("Generating LlamaIndex documents...")
        documents = generate_documents(raw_data, schema, doc_id_key="id")
        logger.info(f"Successfully generated {len(documents)} documents.")
        
        # 3. Run Ingestion Pipeline
        logger.info("Starting ingestion pipeline...")
        result = ingestion_service.ingest(documents, batch_size=2, batch_process=False)
        logger.info(f"Ingestion pipeline completed successfully. Total nodes: {result.total_nodes}")
        
        return {
            "message": "Ingestion successful",
            "source": source,
            "total_nodes_ingested": result.total_nodes,
            "total_documents_processed": result.total_documents
        }
    except Exception as e:
        logger.exception(f"Unexpected error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the document vector store and return a generic response with source nodes.
    """
    if query_service is None:
        raise HTTPException(status_code=503, detail="Query service is not initialized.")
        
    try:
        logger.info("Start the Query")
        response = query_service.query(request)
        return response
    except Exception as e:
        logger.exception(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/query/structured", response_model=FactCheck)
async def query_documents_structured(request: QueryRequest):
    """
    Query the document vector store and return a highly structured FactCheck response.
    """
    if query_service is None:
        raise HTTPException(status_code=503, detail="Query service is not initialized.")
        
    try:
        response = query_service.query_structured(request)
        return response
    except Exception as e:
        logger.exception(f"Structured query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Structured query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI app using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
