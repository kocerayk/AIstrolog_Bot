import logging
import requests
import json
import os
from datetime import datetime, time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from flask import Flask
import threading
import pymongo

# 1. AYARLAR
TOKEN = "8330939722:AAE9dBVLBNpQClQ-OVlKk1hPYfTs6UhJsX4"
GITHUB_BASE_URL = "https://raw.githubusercontent.com/kocerayk/AIstrolog/main/frontend/public/data/summarized_processed_daily_raw_"

# MongoDB Ayarları
# Render'da Environment Variable olarak tanımlanmalı: MONGO_URI
MONGO_URI = os.environ.get("MONGO_URI")

# Eğer MONGO_URI yoksa (lokal test için) uyarı ver veya varsayılan kullan (dikkatli olunmalı)
if not MONGO_URI:
    logging.warning("MONGO_URI bulunamadı! Veritabanı işlemleri çalışmayabilir.")

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["aistrolog_db"]
    subscribers_collection = db["subscribers"]
except Exception as e:
    logging.error(f"MongoDB bağlantı hatası: {e}")
    client = None
    subscribers_collection = None

# Haritalamalar (Kod içi ID -> Ekranda Görünen)
BURC_MAP = {
    'koc': 'Koç', 'boga': 'Boğa', 'ikizler': 'İkizler', 'yengec': 'Yengeç',
    'aslan': 'Aslan', 'basak': 'Başak', 'terazi': 'Terazi', 'akrep': 'Akrep',
    'yay': 'Yay', 'oglak': 'Oğlak', 'kova': 'Kova', 'balik': 'Balık'
}

KATEGORI_MAP = {
    'genel': '💬 Genel',
    'aşk': '❤️ Aşk',
    'para': '💰 Para',
    'sağlık': '⚕️ Sağlık' 
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- YARDIMCI FONKSİYONLAR ---

def get_today_url():
    today_str = datetime.now().strftime('%Y-%m-%d')
    return f"{GITHUB_BASE_URL}{today_str}.json"

def veri_cek():
    url = get_today_url()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logging.error(f"Hata: {e}")
        return None

def abone_yonetimi(chat_id, islem='ekle'):
    """Abone ekleme ve çıkarma işlemleri (MongoDB)"""
    if not subscribers_collection:
        logging.error("Veritabanı bağlantısı yok!")
        return False

    chat_id_int = int(chat_id)
    
    try:
        if islem == 'ekle':
            # Upsert: Varsa güncelle (bir şey değişmez), yoksa ekle
            subscribers_collection.update_one(
                {'chat_id': chat_id_int},
                {'$set': {'chat_id': chat_id_int, 'joined_at': datetime.now()}},
                upsert=True
            )
            return True
        elif islem == 'cikar':
            result = subscribers_collection.delete_one({'chat_id': chat_id_int})
            return result.deleted_count > 0
    except Exception as e:
        logging.error(f"Veritabanı hatası ({islem}): {e}")
        return False
    return False

# --- KLAVYE OLUŞTURUCULAR ---

def ana_menu_klavyesi():
    keyboard = [
        [InlineKeyboardButton("Koç ♈", callback_data='menu_koc'), InlineKeyboardButton("Boğa ♉", callback_data='menu_boga')],
        [InlineKeyboardButton("İkizler ♊", callback_data='menu_ikizler'), InlineKeyboardButton("Yengeç ♋", callback_data='menu_yengec')],
        [InlineKeyboardButton("Aslan ♌", callback_data='menu_aslan'), InlineKeyboardButton("Başak ♍", callback_data='menu_basak')],
        [InlineKeyboardButton("Terazi ♎", callback_data='menu_terazi'), InlineKeyboardButton("Akrep ♏", callback_data='menu_akrep')],
        [InlineKeyboardButton("Yay ♐", callback_data='menu_yay'), InlineKeyboardButton("Oğlak ♑", callback_data='menu_oglak')],
        [InlineKeyboardButton("Kova ♒", callback_data='menu_kova'), InlineKeyboardButton("Balık ♓", callback_data='menu_balik')],
        [InlineKeyboardButton("🌐 Web Sitesini Ziyaret Et", url='https://aistrolog.vercel.app/burclar')]
    ]
    return InlineKeyboardMarkup(keyboard)

def kategori_klavyesi(burc_kod):
    # burc_kod örnek: 'koc'
    keyboard = [
        [InlineKeyboardButton("💬 Genel", callback_data=f'oku_{burc_kod}_genel'), InlineKeyboardButton("❤️ Aşk", callback_data=f'oku_{burc_kod}_aşk')],
        [InlineKeyboardButton("💰 Para", callback_data=f'oku_{burc_kod}_para'), InlineKeyboardButton("⚕️ Sağlık", callback_data=f'oku_{burc_kod}_sağlık')],
        [InlineKeyboardButton("🔮 Burçlara Dön", callback_data='ana_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def geri_donus_klavyesi(burc_kod):
    keyboard = [
        [InlineKeyboardButton("☰ Kategorilere Dön", callback_data=f'menu_{burc_kod}')],
        [InlineKeyboardButton("🔮 Burçlara Dön", callback_data='ana_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- HANDLER FONKSİYONLARI ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    abone_yonetimi(chat_id, 'ekle')
    
    mesaj = (
        f"Merhaba {user.first_name}! 🌙\n"
        "AIstrolog Yapay zeka destekli astroloji servisine hoş geldin!\n"
        "Her gün 12:00'de günlük burç yorumun bildiriminde.\n\n"
        "Bildirim almak istemiyorsan /stop yazabilirsin.\n"
        "Günlük Burç Özetini görüntülemek için burcunu seç:"
    )
    await update.message.reply_text(mesaj, reply_markup=ana_menu_klavyesi())

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    basarili = abone_yonetimi(chat_id, 'cikar')
    
    if basarili:
        await update.message.reply_text("Abonelikten çıktın. Artık günlük özet bildirimleri almayacaksın:(")
    else:
        await update.message.reply_text("Zaten abone değilsin.")

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data # Örn: 'ana_menu', 'menu_koc', 'oku_koc_ask'
    
    # 1. ANA MENÜYE DÖNÜŞ
    if data == 'ana_menu':
        await query.edit_message_text(
            text="Günlük Burç Özetini görüntülemek için burcunu seç:",
            reply_markup=ana_menu_klavyesi()
        )
        return

    # 2. BURÇ SEÇİLDİ -> KATEGORİ GÖSTER (Format: menu_koc)
    if data.startswith('menu_'):
        burc_kod = data.split('_')[1] # 'koc'
        burc_ismi = BURC_MAP.get(burc_kod)
        
        await query.edit_message_text(
            text=f"Sevgili {burc_ismi}, hangi yorumu okumak istersin?",
            reply_markup=kategori_klavyesi(burc_kod),
            parse_mode='Markdown'
        )
        return

    # 3. KATEGORİ SEÇİLDİ -> YORUM OKU (Format: oku_koc_ask)
    if data.startswith('oku_'):
        _, burc_kod, kategori = data.split('_') 
        burc_ismi = BURC_MAP.get(burc_kod)
        
        await query.edit_message_text(text=f"🔮 {burc_ismi} burcu için veriler çekiliyor...")
        
        veriler = veri_cek()
        
        if veriler and burc_ismi in veriler:
            # JSON'dan veriyi al
            yorum = veriler[burc_ismi].get(kategori, "Bu kategori için veri bulunamadı.")
            
            baslik_ikon = KATEGORI_MAP.get(kategori, kategori.capitalize())
            
            mesaj = (
                f"🌟 **{burc_ismi} Burcu - {baslik_ikon} Yorumu** 🌟\n\n"
                f"{yorum}\n"
            )
        else:
            mesaj = "⚠️ Bugünün verileri henüz yüklenmemiş veya bir hata oluştu."

        await query.edit_message_text(
            text=mesaj,
            reply_markup=geri_donus_klavyesi(burc_kod),
            parse_mode='Markdown'
        )

# --- GÜNLÜK BİLDİRİM ---

async def gunluk_bildirim_gorevi(context: ContextTypes.DEFAULT_TYPE):
    if not subscribers_collection:
        return

    try:
        # Tüm aboneleri çek
        cursor = subscribers_collection.find({})
        for doc in cursor:
            chat_id = doc.get('chat_id')
            if chat_id:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="🔔 Günlük burç yorumların hazır! Okumak için tıkla:",
                        reply_markup=ana_menu_klavyesi()
                    )
                except Exception as e:
                    logging.error(f"Bildirim hatası ({chat_id}): {e}")
    except Exception as e:
        logging.error(f"Veritabanı okuma hatası: {e}")

# --- FLASK SERVER (Render İçin) ---

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    # Flask sunucusunu ayrı bir thread'de başlat
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop)) 
    application.add_handler(CallbackQueryHandler(buton_tiklama))
    
    # Zamanlayıcı
    job_queue = application.job_queue
    turkey_tz = pytz.timezone("Europe/Istanbul")
    target_time = time(hour=12, minute=0, second=0, tzinfo=turkey_tz)
    
    job_queue.run_daily(gunluk_bildirim_gorevi, time=target_time)
    
    print("Bot çalışıyor...")
    application.run_polling()