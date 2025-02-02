# Telegram AI Agent

A Telegram bot that processes audio messages using RAG (Retrieval-Augmented Generation) and LLM technologies. The bot transcribes audio, analyzes content against a knowledge base, and provides relevant responses.

## Features
- Audio message processing using OpenAI Whisper
- RAG system implementation with Pinecone vector database
- Document processing support (PDF, DOCX, XLSX, PPTX)
- LLM integration with GPT-4
- Comprehensive error handling and logging

- 🎤 Обробка голосових повідомлень за допомогою OpenAI Whisper
- 🔍 RAG система з використанням векторної бази даних Pinecone
- 📄 Підтримка різних форматів документів:
  - PDF файли (.pdf)
  - Word документи (.doc, .docx)
  - Excel таблиці (.xlsx)
  - PowerPoint презентації (.pptx)
  - Текстові файли (.txt, .md)
- 🤖 Інтеграція з GPT-4 для генерації відповідей
- 📊 Комплексна обробка помилок та логування
- 🇺🇦 Повна підтримка української мови

## Prerequisites


- Telegram Bot Token
- OpenAI API Key
- Pinecone API Key and Environment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tg-ai-agent.git
cd tg-ai-agent
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the environment template and fill in your values:
```bash
cp .env.example .env
```

## Project structure

```
tg-ai-agent/
├── src/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py    # Сервіс для роботи з OpenAI API
│   │   ├── pinecone_service.py  # Сервіс для роботи з Pinecone
│   │   └── rag_service.py       # Основний RAG сервіс
│   ├── bot.py                   # Telegram бот
│   └── main.py                  # Точка входу в додаток
├── logs/                        # Директорія для логів
├── .env.example                 # Шаблон змінних середовища
├── .gitignore
├── requirements.txt             # Залежності проекту
└── README.md
```

## Налаштування

У файлі `.env` необхідно вказати:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST=your_pinecone_host
PINECONE_INDEX_NAME=your_index_name

# Додаткові налаштування
MAX_AUDIO_LENGTH=300
MAX_TOKENS_RESPONSE=1000
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
LOG_LEVEL=INFO
```

## Використання

1. Запустіть бота:
```bash
python src/main.py
```

2. В Telegram:
   - Відправте команду `/start` для початку роботи
   - Використовуйте кнопку "⚙️ Налаштування" для керування базою знань
   - Надсилайте голосові повідомлення з питаннями
   - Завантажуйте документи для навчання бота

## Логування