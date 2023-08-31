from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters
import requests
import asyncio
import httpx

# Your FastAPI endpoints
FASTAPI_BASE_URL = "http://localhost:8900"

# Telegram Bot API token
TELEGRAM_TOKEN = 'YOUR_API_HERE'

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Lagrange's Q&A chatbot! Send /help for instructions.")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("You can ask questions using the /ask command.")

async def ask_command(update: Update, context: CallbackContext):
    question = " ".join(context.args)
    
    # Extract session_id (use Telegram ID as session ID) and project from update
    session_id = str(update.message.from_user.id)
    project = "testing_qa"
    
    # Send request to FastAPI endpoint to get answer
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{FASTAPI_BASE_URL}/answer", params={"session_id": session_id, "project": project, "question": question})
    
    if response.status_code == 200:
        response_data = response.json()

        # Check if the first element of the response is a dictionary
        if isinstance(response_data[0], dict):
            # Extract the 'msg' key, which seems to contain the answer
            answer = response_data[0].get('msg')
            if answer:
                await update.message.reply_text(answer)
            else:
                print("No 'msg' key found in the response.")
                await update.message.reply_text("Failed to get answer.")
        else:
            print(f"Unexpected response format: {response_data}")
            await update.message.reply_text("Failed to get answer.")
        
async def message_handler(update: Update, context: CallbackContext):
    message_text = update.message.text
    if message_text.startswith("/ask"):
        await ask_command(update, context)
    else:
        await update.message.reply_text("Unknown command. Send /help for instructions.")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
