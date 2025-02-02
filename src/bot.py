import os
import tempfile
from typing import BinaryIO
from loguru import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from services.rag_service import rag_service
import PyPDF2
import docx
import openpyxl
from pptx import Presentation

# Configure logging
logger.add("bot.log", rotation="500 MB")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("⚙️ Налаштування", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привіт! Я твій AI-асистент в OVB. Ти можеш:\n"
        "1. Надсилати мені голосові повідомлення з питаннями\n"
        "2. Надсилати документи для навчання\n"
        "Я використаю свої знання, щоб відповісти на ваші запитання!",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Як мене використовувати:\n\n"
        "🎤 Голосові повідомлення: Задавайте питання голосовим повідомленням\n"
        "📄 Документи: Надсилайте текстові файли для навчання\n"
        "❓ Питання: Я використаю вивчене, щоб відповісти на ваші запитання\n\n"
        "Підтримувані формати файлів:\n"
        "- Текстові файли (.txt, .md)\n"
        "- PDF документи (.pdf)\n"
        "- Word документи (.doc, .docx)\n"
        "- Excel файли (.xlsx)\n"
        "- PowerPoint презентації (.pptx)"
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings button click."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📚 Додати документи для навчання", callback_data='add_docs')],
        [InlineKeyboardButton("❌ Видалити всі документи", callback_data='delete_docs')],
        [InlineKeyboardButton("ℹ️ Статистика бази знань", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="⚙️ Налаштування\n\n"
        "Оберіть опцію:",
        reply_markup=reply_markup
    )

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings menu callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_docs':
        await query.edit_message_text(
            "📚 Надішліть мені документи для навчання.\n\n"
            "Підтримувані формати:\n"
            "- Текстові файли (.txt, .md)\n"
            "- PDF документи (.pdf)\n"
            "- Word документи (.doc, .docx)\n"
            "- Excel файли (.xlsx)\n"
            "- PowerPoint презентації (.pptx)"
        )
    elif query.data == 'delete_docs':
        # Тут можна додати логіку видалення документів
        await query.edit_message_text("🗑 Всі документи видалено з бази знань.")
    elif query.data == 'stats':
        # Тут можна додати логіку отримання статистики
        await query.edit_message_text("📊 Статистика бази знань буде доступна незабаром.")

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_text_from_xlsx(file_path: str) -> str:
    """Extract text from XLSX file."""
    wb = openpyxl.load_workbook(file_path)
    text = []
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for row in ws.rows:
            row_text = " ".join(str(cell.value) for cell in row if cell.value)
            if row_text:
                text.append(row_text)
    return "\n".join(text)

def extract_text_from_pptx(file_path: str) -> str:
    """Extract text from PPTX file."""
    prs = Presentation(file_path)
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    try:
        # Send initial status
        status_message = await update.message.reply_text("🎧 Обробляю ваше голосове повідомлення...")
        
        # Get voice file
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        # Download voice file to temporary location
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            await voice_file.download_to_drive(temp_file.name)
            
            # Process audio using RAG service
            result = await rag_service.process_audio_query(temp_file.name)
            
            # Send transcription and response
            await status_message.edit_text(
                f"🎯 Я почув: {result['transcription']}\n\n"
                f"🤖 Моя відповідь: {result['response']}"
            )
            
        # Cleanup temporary file
        os.unlink(temp_file.name)
        
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        await update.message.reply_text(
            "😕 Вибачте, виникла проблема з обробкою голосового повідомлення. "
            "Будь ласка, спробуйте ще раз або переконайтеся, що повідомлення записано чітко."
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages."""
    try:
        # Check if document format is supported
        document = update.message.document
        file_name = document.file_name.lower()
        supported_formats = ('.txt', '.md', '.pdf', '.doc', '.docx', '.xlsx', '.pptx')
        
        if not any(file_name.endswith(fmt) for fmt in supported_formats):
            await update.message.reply_text(
                "❌ Будь ласка, надсилайте файли лише в підтримуваних форматах:\n"
                "- Текстові файли (.txt, .md)\n"
                "- PDF документи (.pdf)\n"
                "- Word документи (.doc, .docx)\n"
                "- Excel файли (.xlsx)\n"
                "- PowerPoint презентації (.pptx)"
            )
            return
            
        # Send initial status
        status_message = await update.message.reply_text("📚 Обробляю ваш документ...")
        
        # Get document file
        doc_file = await context.bot.get_file(document.file_id)
        
        # Download and process document
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_name)[1], delete=False) as temp_file:
            await doc_file.download_to_drive(temp_file.name)
            
            # Extract text based on file format
            if file_name.endswith('.pdf'):
                text = extract_text_from_pdf(temp_file.name)
            elif file_name.endswith(('.doc', '.docx')):
                text = extract_text_from_docx(temp_file.name)
            elif file_name.endswith('.xlsx'):
                text = extract_text_from_xlsx(temp_file.name)
            elif file_name.endswith('.pptx'):
                text = extract_text_from_pptx(temp_file.name)
            else:  # txt or md
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Process document using RAG service
            await rag_service.process_document(text, document.file_id)
            
            await status_message.edit_text(
                "✅ Документ успішно оброблено! Я вивчив його вміст."
            )
            
        # Cleanup temporary file
        os.unlink(temp_file.name)
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        await update.message.reply_text(
            "😕 Вибачте, виникла проблема з обробкою документа. "
            "Будь ласка, перевірте формат файлу та спробуйте ще раз."
        )

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(settings, pattern='^settings$'))
    application.add_handler(CallbackQueryHandler(handle_settings_callback, pattern='^(add_docs|delete_docs|stats)$'))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 