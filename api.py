from fastapi import FastAPI, Form, HTTPException, Header, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Annotated, List, Optional, Dict, Any
import asyncio
import tempfile
import os
import re
import logging
import sys
from examples.insert_custom_kg import build_kg, csv_to_json_list, pcap_to_json_list
from agent import (
    generate_enriched_playbooks,
    fetch_sample_links,
    generate_visual_graph,
    initialize_rag_deepseek,
    fetch_all_playbooks,
    current_model_complete,
    initialize_rag_ollama,
)
import json
import time
from datetime import datetime

from lightrag import LightRAG, QueryParam

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("api.log")],
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting Threat Hunting API server...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")


async def fetch_graph_folders_names_from_os():
    """Fetch the names of the folders in the custom_kg directory."""
    return os.listdir("./AppDbStore")


async def determine_entity_type(
    value: str, available_columns: List[str], flow: Dict[str, Any]
) -> str:
    """Automatically determine the entity type based on the value and available data."""
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value):
        return "IP Address"
    if value.isdigit() and 0 <= int(value) <= 65535:
        return "Port"
    if "Protocol" in flow and value == flow["Protocol"]:
        return "Protocol"
    if "Service" in flow and value == flow["Service"]:
        return "Service"
    if re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z0-9][a-zA-Z0-9-]*)*$", value):
        return "Hostname"
    if "class" in value.lower() or "type" in value.lower():
        return "Traffic Class"
    return "Network Entity"


app = FastAPI(
    title="Threat Hunting API",
    description="API for threat hunting and malware analysis using RAG",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React app port
        "http://localhost:80",  # Nginx container port
        "http://localhost:5173",  # Vite dev server default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlaybookRequest(BaseModel):
    year: str = "2013"
    max_samples: int = 3


class PlaybookResponse(BaseModel):
    playbooks: List[Dict]


class ExtractPlaybookRequest(BaseModel):
    url: str


class ExtractPlaybookResponse(BaseModel):
    playbook: Dict


class SampleLinksRequest(BaseModel):
    year: str = "2013"
    max_samples: int = 5


class SampleLinksResponse(BaseModel):
    links: List[str]


class GraphDataResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class BuildKGResponse(BaseModel):
    message: str
    entity_count: int
    relationship_count: int
    entity_types: List[str]


class GraphQueryRequest(BaseModel):
    query: str
    working_dir: str = "./custom_kg"


class ChatRequest(BaseModel):
    query: str
    dir_path: str = "./custom_kg"
    conversation_history: Optional[List[Dict[str, str]]] = None


class GraphFoldersNamesResponse(BaseModel):
    folders: List[str]


class GraphDataRequest(BaseModel):
    dir_path: str = "./custom_kg"


@app.get("/")
async def root():
    return {"message": "Welcome to the Threat Hunting API"}


@app.get("/test-hot-reload")
async def test_hot_reload():
    """Test endpoint to verify hot reload is working."""
    return {
        "message": "Hot reload test - version 1!!!",
        "timestamp": str(datetime.now()),
    }


@app.get("/fetch-all-playbooks", response_model=List[Dict[str, Any]])
async def get_all_playbooks(year: str = "2013", max_samples: int = 2):
    """Fetch and process all playbooks from malware analysis blog."""
    try:
        return await fetch_all_playbooks(year=year, max_samples=max_samples)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph-folders-names", response_model=GraphFoldersNamesResponse)
async def get_graph_folders_names():
    """Get the names of the folders in the custom_kg directory."""
    try:
        folders = await fetch_graph_folders_names_from_os()
        return GraphFoldersNamesResponse(folders=folders)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph-data", response_model=GraphDataResponse)
async def get_graph_data(
    dir_path: str = "./custom_kg",
):
    """Get graph data for visualization."""
    try:
        logger.info(f"Generating graph data for directory: {dir_path}")
        graph_data = await generate_visual_graph(dir_path=dir_path)
        return GraphDataResponse(**graph_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build-kg", response_model=BuildKGResponse)
async def build_knowledge_graph(
    file: UploadFile = File(...),
    source_column: Annotated[str, Form()] = "Source IP",
    target_column: Annotated[str, Form()] = "Destination IP",
    relationship_columns: Annotated[Optional[List[str]], Form()] = None,
    working_dir: Annotated[str, Form()] = "./custom_kg",
):
    """
    Build a knowledge graph from an uploaded CSV or PCAP file.

    Args:
        file: The uploaded file (CSV or PCAP)
        source_column: Column name for source entity
        target_column: Column name for target entity
        relationship_columns: Optional list of columns to include in relationships
        working_dir: Directory to store the knowledge graph data
    """
    try:
        # Create working directory if it doesn't exist
        os.makedirs(working_dir, exist_ok=True)

        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Initialize RAG
        rag = await initialize_rag_ollama(working_dir=working_dir)
        print(f"working_dir: {working_dir}")
        # Process the file based on its extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext == ".csv":
            flows = await csv_to_json_list(temp_file_path, max_rows=200)
        elif file_ext == ".pcap":
            flows = await pcap_to_json_list(temp_file_path, max_rows=2000)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a CSV or PCAP file.",
            )

        # Build the knowledge graph
        await build_kg(
            flows=flows,
            rag=rag,
            source_column=source_column,
            target_column=target_column,
            relationship_columns=relationship_columns,
        )

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # Get the entity types from the built graph
        entity_types = set()
        for flow in flows:
            for endpoint in [flow.get(source_column), flow.get(target_column)]:
                if endpoint:
                    entity_type = await determine_entity_type(
                        endpoint, list(flow.keys()), flow
                    )
                    entity_types.add(entity_type)

        return BuildKGResponse(
            message=f"Knowledge graph built successfully in {working_dir}",
            entity_count=len(
                set(flow.get(source_column) for flow in flows)
                | set(flow.get(target_column) for flow in flows)
            ),
            relationship_count=len(flows),
            entity_types=list(entity_types),
        )

    except Exception as e:
        # Clean up the temporary file in case of error
        if "temp_file_path" in locals():
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))


async def stream_response(response: str):
    """Stream the response word by word with a small delay."""
    logger.info("Starting stream_response function")
    try:
        # If response is a string, split it into words
        if isinstance(response, str):
            logger.info(f"Processing string response of length: {len(response)}")
            words = response.split()
            logger.info(f"Split into {len(words)} words")
            for word in words:
                yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                await asyncio.sleep(0.05)
        # If response is already a generator, yield its chunks
        else:
            logger.info("Processing generator response")
            async for chunk in response:
                if chunk:
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
                    await asyncio.sleep(0.05)
    except Exception as e:
        logger.error(f"Error in stream_response: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'token': f'Error: {str(e)}'})}\n\n"
    finally:
        logger.info("Streaming completed, sending [DONE]")
        yield "data: [DONE]\n\n"


@app.post("/query-graph")
async def query_graph(request: GraphQueryRequest):
    """
    Query the knowledge graph using natural language with streaming response.

    Args:
        query: The natural language query about the graph
        working_dir: Directory containing the knowledge graph data
    """
    try:
        # Initialize RAG
        rag = await initialize_rag_deepseek(working_dir=request.working_dir)

        # Query using RAG with global mode
        response = await rag.aquery(request.query, param=QueryParam(mode="global"))

        return StreamingResponse(
            stream_response(response), media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def query_stream(request: ChatRequest):
    """
    Stream a response to a chat query.
    """
    logger.info(f"Received streaming query request: {request.query}")
    logger.info(f"Directory path: {request.dir_path}")
    logger.info(
        f"Conversation history length: {len(request.conversation_history) if request.conversation_history else 0}"
    )

    try:
        logger.info("Initializing RAG with Ollama...")
        # Initialize RAG with Ollama instead of DeepSeek
        rag = await initialize_rag_deepseek(working_dir=request.dir_path)
        logger.info("RAG initialization completed successfully")

        logger.info("Executing query with RAG...")
        # Query using RAG with global mode
        response = await rag.aquery(
            request.query,
            param=QueryParam(
                mode="hybrid", conversation_history=request.conversation_history
            ),
        )

        logger.info(f"Response type: {type(response)}")
        logger.info(
            f"Response content preview: {response[:100] if isinstance(response, str) else 'generator'}"
        )

        logger.info("Creating streaming response...")
        return StreamingResponse(
            stream_response(response),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error(f"Error in query_stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)
