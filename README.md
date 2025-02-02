# Telegram AI Agent

A Telegram bot that processes audio messages using RAG (Retrieval-Augmented Generation) and LLM technologies. The bot transcribes audio, analyzes content against a knowledge base, and provides relevant responses.

## Features
- 🎤 **Voice Message Processing**: Convert voice messages to text and analyze client information
- 📄 **Document Processing**: Learn from various document formats (PDF, Word, Excel, PowerPoint)
- 👥 **Client Management**: Save and edit client information automatically
- 🤖 **AI-Powered Responses**: Generate structured responses using GPT-4
- 📊 **RAG Integration**: Utilize Retrieval-Augmented Generation for accurate responses

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

## Supported File Formats

- Text files (.txt, .md)
- PDF documents (.pdf)
- Word documents (.doc, .docx)
- Excel spreadsheets (.xlsx)
- PowerPoint presentations (.pptx)

- Telegram Bot Token
- OpenAI API Key
- Pinecone API Key and Environment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tg_ai_agent.git
cd tg_ai_agent
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

## Usage

1. Start the bot:
```bash
python src/bot.py
```

2. In Telegram:
   - Start a chat with the bot using `/start`
   - Send voice messages for client interactions
   - Upload documents for the bot to learn from
   - Manage client information using inline buttons

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

## Contributing

1. Запустіть бота:
```bash
python src/main.py
```

2. В Telegram:
   - Відправте команду `/start` для початку роботи
   - Використовуйте кнопку "⚙️ Налаштування" для керування базою знань
   - Надсилайте голосові повідомлення з питаннями
   - Завантажуйте документи для навчання бота

This project is licensed under the MIT License - see the LICENSE file for details.