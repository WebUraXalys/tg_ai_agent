import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone, Index
from loguru import logger

load_dotenv()

class PineconeService:
    def __init__(self):
        self._validate_config()
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(host=os.getenv("PINECONE_HOST"))
        logger.info("Pinecone client initialized successfully")

    def _validate_config(self):
        required_vars = [
            "PINECONE_API_KEY",
            "PINECONE_HOST",
            "PINECONE_INDEX_NAME"
        ]
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")

    async def initialize_index(self):
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Successfully connected to Pinecone index: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error connecting to index: {str(e)}")
            raise

    async def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """
        Upsert vectors to Pinecone index
        vectors: List of dictionaries with 'id', 'values', and optional 'metadata'
        """
        try:
            response = self.index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted {len(vectors)} vectors")
            return response
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            raise

    async def query_vectors(self, vector: List[float], top_k: int = 3):
        """
        Query vectors from Pinecone index
        vector: Query vector
        top_k: Number of results to return
        """
        try:
            response = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            return response.matches
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            raise

    async def delete_vectors(self, ids: List[str]):
        """
        Delete vectors from Pinecone index
        ids: List of vector IDs to delete
        """
        try:
            self.index.delete(ids=ids)
            logger.info(f"Successfully deleted {len(ids)} vectors")
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise

# Create singleton instance
pinecone_service = PineconeService() 