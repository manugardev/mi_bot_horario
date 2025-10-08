import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Cargar variables de entorno
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
HORARIO_FILE = "horario.txt"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Soy tu bot de horario. Usa /horario para ver tus clases.")

async def horario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(HORARIO_FILE):
        await update.message.reply_text("⚠️ No se encontró el archivo de horario.")
        return

    now = datetime.now()
    dia = now.strftime("%A").lower()

    with open(HORARIO_FILE, "r", encoding="utf-8") as file:
        lineas = file.readlines()

    mensaje = f"📅 Horario para *{dia.capitalize()}*:\n"
    encontrado = False
    for linea in lineas:
        if linea.lower().startswith(dia):
            mensaje += linea
            encontrado = True

    if not encontrado:
        mensaje = "⛔ No hay clases programadas para hoy."

    await update.message.reply_text(mensaje, parse_mode="Markdown")

def main():
    """No usamos asyncio.run() porque Render ya gestiona el bucle."""
    logging.info("🤖 Iniciando bot...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("horario", horario))

    logging.info("🤖 Bot en marcha en Render...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()


