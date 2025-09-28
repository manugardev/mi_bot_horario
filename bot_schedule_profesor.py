import json
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os

# Cargar token de .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ ERROR: Define BOT_TOKEN en .env")

# Mapeo de días en español a inglés (usado por datetime)
SPANISH_DAY = {
    "lunes": "monday",
    "martes": "tuesday",
    "miércoles": "wednesday",
    "miercoles": "wednesday",
    "jueves": "thursday",
    "viernes": "friday"
}

# Cargar el horario compartido
def load_schedules():
    with open("schedules.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Obtener el horario para un día concreto
def get_schedule_for_day(day: str):
    schedules = load_schedules()  # Ahora schedules es único para todos
    tz = pytz.timezone(schedules["timezone"])
    
    if day.lower() == "hoy":
        day_name = datetime.now(tz).strftime("%A").lower()
    elif day.lower() == "mañana":
        day_name = (datetime.now(tz) + timedelta(days=1)).strftime("%A").lower()
    else:
        day_name = SPANISH_DAY.get(day.lower())
    
    if not day_name:
        return None
    
    return schedules["schedule"].get(day_name, [])

# Handler para /horario_hoy
async def horario_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    schedule = get_schedule_for_day("hoy")
    if not schedule:
        await update.message.reply_text("❌ No hay horario guardado para hoy.")
        return
    text = "\n".join([f"{s['time']} - {s['subject']}" for s in schedule])
    await update.message.reply_text(f"📅 Horario de hoy:\n{text}")

# Handler para /horario_manana
async def horario_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    schedule = get_schedule_for_day("mañana")
    if not schedule:
        await update.message.reply_text("❌ No hay horario guardado para mañana.")
        return
    text = "\n".join([f"{s['time']} - {s['subject']}" for s in schedule])
    await update.message.reply_text(f"📅 Horario de mañana:\n{text}")

# Handler para /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hola! Soy tu bot de horario compartido.\n\n"
        "Puedes consultar el horario de hoy, mañana o cualquier día escribiendo:\n"
        "lunes, martes, miércoles, jueves, viernes, hoy o mañana.\n\n"
        "También puedes usar los comandos:\n"
        "/horario_hoy\n/horario_manana"
    )

# Handler para mensajes de texto directo
async def mensaje_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().lower()
    
    if texto in SPANISH_DAY or texto in ["hoy", "mañana"]:
        schedule = get_schedule_for_day(texto)
        if not schedule:
            await update.message.reply_text(f"❌ No hay horario guardado para {texto}.")
            return
        text = "\n".join([f"{s['time']} - {s['subject']}" for s in schedule])
        await update.message.reply_text(f"📅 Horario de {texto}:\n{text}")
    else:
        await update.message.reply_text(
            "❌ No te entiendo. Escribe un día de la semana, 'hoy' o 'mañana'."
        )

# Función principal
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("horario_hoy", horario_hoy))
    app.add_handler(CommandHandler("horario_manana", horario_manana))
    
    # Mensajes de texto directo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_dia))
    
    print("🤖 Bot en marcha... Pulsa Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
