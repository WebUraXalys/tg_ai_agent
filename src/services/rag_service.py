import os
from typing import List, Dict, Any
from loguru import logger
from .openai_service import openai_service
from .pinecone_service import pinecone_service

class RAGService:
    def __init__(self):
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
        logger.info("RAG service initialized successfully")

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        words = text.split()
        chunk_size_words = self.chunk_size // 4  # Approximate words per chunk
        
        for i in range(0, len(words), chunk_size_words - self.chunk_overlap):
            chunk = " ".join(words[i:i + chunk_size_words])
            chunks.append(chunk)
        
        return chunks

    async def process_document(self, text: str, document_id: str):
        """Process a document and store it in the vector database"""
        try:
            # Split text into chunks
            chunks = self._chunk_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Create embeddings for chunks
            embeddings = await openai_service.create_embeddings(chunks)
            logger.info("Created embeddings for chunks")

            # Prepare vectors for Pinecone
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vectors.append({
                    "id": f"{document_id}_chunk_{i}",
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "document_id": document_id
                    }
                })

            # Store vectors in Pinecone
            await pinecone_service.upsert_vectors(vectors)
            logger.info(f"Stored {len(vectors)} vectors in Pinecone")

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    async def process_audio_query(self, audio_file_path: str) -> str:
        """Process audio query and return response"""
        try:
            # Transcribe audio
            transcription = await openai_service.transcribe_audio(audio_file_path)
            logger.info(f"Transcribed audio: {transcription}")

            # Create embedding for query
            query_embedding = await openai_service.create_embeddings([transcription])
            logger.info("Created embedding for query")

            # Search similar vectors
            matches = await pinecone_service.query_vectors(query_embedding[0], top_k=3)
            logger.info(f"Found {len(matches)} similar vectors")

            # Combine context from matches
            context = "\n\n".join([match.metadata["text"] for match in matches])

            # Generate response
            response = await openai_service.generate_response(transcription, context)
            logger.info("Generated response")

            return {
                "transcription": transcription,
                "response": response
            }

        except Exception as e:
            logger.error(f"Error processing audio query: {str(e)}")
            raise

# Create singleton instance
rag_service = RAGService() 