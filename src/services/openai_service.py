import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class OpenAIService:
    def __init__(self):
        self._validate_config()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("OpenAI client initialized successfully")

    def _validate_config(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Missing required environment variable: OPENAI_API_KEY")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Whisper API
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return response.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    async def generate_response(self, query: str, context: str) -> str:
        """
        Generate response using GPT-4 with context
        """
        try:
            messages = [
                {"role": "system", "content": "Ти - корисний помічник фінансового консультанта компанії OVB, з доступом до бази знань продуктів компаній партенрів. Використовуйте наданий контекст для точних відповідей на запитання. Якщо відповідь не відповідає контексту, скажіть про це чітко.У віддповідь я очікую побачити які з пропозицій ринку найкраще підходять для мого клієнну. А також на початку короткий опис клієнта."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=int(os.getenv("MAX_TOKENS_RESPONSE", "600"))
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

# Create singleton instance
openai_service = OpenAIService() 