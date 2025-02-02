import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime
from .database_service import database_service

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

    def _extract_client_info(self, response_text: str) -> Dict[str, Any]:
        """Extract client information from the response text"""
        try:
            lines = response_text.split('\n')
            client_info = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Клієнт:'):
                    client_info['full_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('Вік:'):
                    age_text = line.split(':', 1)[1].strip()
                    client_info['age'] = int(''.join(filter(str.isdigit, age_text)))
                elif line.startswith('Дата:'):
                    client_info['meeting_date'] = line.split(':', 1)[1].strip()
                elif line.startswith('Тип зустрічі:'):
                    client_info['meeting_type'] = line.split(':', 1)[1].strip()
                elif line.startswith('Продукт:'):
                    client_info['product_type'] = line.split(':', 1)[1].strip()
                elif line.startswith('Ціль:'):
                    client_info['goal'] = line.split(':', 1)[1].strip()
                elif line.startswith('Опис клієнта:'):
                    description_start = lines.index(line) + 1
                    description_lines = []
                    for desc_line in lines[description_start:]:
                        if desc_line.strip() and not desc_line.startswith('###'):
                            description_lines.append(desc_line.strip())
                        else:
                            break
                    client_info['description'] = ' '.join(description_lines)
                    break
            
            return client_info
        except Exception as e:
            logger.error(f"Error extracting client info: {str(e)}")
            return None

    async def generate_response(self, query: str, context: str) -> str:
        """
        Generate structured response using GPT-4 with context and save client info
        """
        try:
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            system_prompt = """Ти - корисний помічник фінансового консультанта компанії OVB, з доступом до бази знань продуктів компаній партнерів. 
            Використовуй наданий контекст для точних відповідей на запитання. Якщо відповідь не відповідає контексту, скажи про це чітко.

            Твоя відповідь повинна мати наступну структуру:

            1. Інформація про клієнта
            Клієнт: [ім'я та прізвище]
            Вік: [вік] років
            Дата: [поточна дата]
            Тип зустрічі: [тип зустрічі]
            Продукт: [тип продукту]
            Ціль: [мета клієнта]

            Опис клієнта:
            [детальний опис клієнта та його потреб]

            2. Пропозиції продукту
            ### Найкращі пропозиції на ринку:

            #### 1. [Назва програми/компанії]:
            - **Мета**: [основна мета програми]
            - **Переваги**:
              - *[перевага 1]*
              - *[перевага 2]*
              [...]

            [Додатковий коментар щодо програми]"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nQuery: {query}\n\nCurrent date: {current_date}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=int(os.getenv("MAX_TOKENS_RESPONSE", "600"))
            )
            
            response_text = response.choices[0].message.content
            
            # Extract and save client information
            client_info = self._extract_client_info(response_text)
            if client_info:
                await database_service.save_client(client_info)
            
            return response_text
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

# Create singleton instance
openai_service = OpenAIService() 