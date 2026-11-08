import os, subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "9172774227:AAEqIPGoUt2Fn2Zu_C0Mv66NbJvPG69enp8"
setting = {}

def parse_waktu(s):
    s = s.strip()
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    return int(s)

def get_set(uid):
    if uid not in setting:
        setting[uid] = {"mulai": 0, "sampai": 90, "durasi": 90}
    return setting[uid]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim link YouTube, nanti aku potongin.\n\n/durasi 90\n/mulai 5:30\n/sampai 7:00\n/reset")

async def set_durasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        d = int(context.args[0])
        s = get_set(update.effective_user.id)
        s["durasi"] = d
        s["mulai"] = 0
        s["sampai"] = d
        await update.message.reply_text(f"Oke! Dipotong 0:00 sampai {d} detik")
    except:
        await update.message.reply_text("Cara pakai: /durasi 90")

async def set_mulai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        d = parse_waktu(context.args[0])
        s = get_set(update.effective_user.id)
        s["mulai"] = d
        await update.message.reply_text(f"Oke! Mulai dari {context.args[0]}")
    except:
        await update.message.reply_text("Cara pakai: /mulai 5:30")

async def set_sampai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        d = parse_waktu(context.args[0])
        s = get_set(update.effective_user.id)
        s["sampai"] = d
        await update.message.reply_text(f"Oke! Sampai {context.args[0]}. Kirim link YouTube-nya!")
    except:
        await update.message.reply_text("Cara pakai: /sampai 7:00")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    setting[update.effective_user.id] = {"mulai": 0, "sampai": 90, "durasi": 90}
    await update.message.reply_text("Udah di-reset!")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Kirim link YouTube ya!")
        return
    s = get_set(update.effective_user.id)
    mulai = s["mulai"]
    sampai = s["sampai"]
    if sampai <= mulai:
        sampai = mulai + s["durasi"]
    durasi = sampai - mulai
    await update.message.reply_text(f"Siap! Dipotong {mulai}-{sampai} detik. Tunggu 1-3 menit.")
    try:
        for f in ["input.mp4", "klip.mp4"]:
            if os.path.exists(f):
                os.remove(f)
        subprocess.run(["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4", "-o", "input.mp4", url], check=True)
        subprocess.run(["ffmpeg", "-y", "-ss", str(mulai), "-i", "input.mp4", "-t", str(durasi), "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-b:a", "128k", "klip.mp4"], check=True)
        await update.message.reply_video(video=open("klip.mp4", "rb"), caption=f"Klip {mulai}-{sampai} detik selesai!")
    except Exception as e:
        await update.message.reply_text(f"Gagal: {e}")

if __name__ == "__main__":
    print("Bot jalan...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("durasi", set_durasi))
    app.add_handler(CommandHandler("mulai", set_mulai))
    app.add_handler(CommandHandler("sampai", set_sampai))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()
