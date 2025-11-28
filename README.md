# AIstrolog Bot 🌙

Bu proje, **AIstrolog** projesinden günlük burç yorumlarını çeken ve Telegram üzerinden kullanıcılara sunan bir bottur.

## Özellikler

- **Günlük Burç Yorumları:** Her gün https://aistrolog.vercel.app/burclar sitesinin sağladığı verilerle güncellenen burç yorumlarını takip edebilirsiniz. Veri kaynağını inceleyebileceğiniz repo: https://github.com/kocerayk/AIstrolog
- **Kategoriler:** Genel, Aşk, Para ve Sağlık kategorilerinde özel yorumlar.
- **Günlük Bildirimler:** Her gün saat 12:00'de otomatik bildirim.
- **Web Entegrasyonu:** AIstrolog web sitesine hızlı erişim.
- **7/24 Aktif:** Render üzerinde Web Service olarak çalışır.
- **Veritabanı:** Kullanıcı verileri MongoDB üzerinde saklanır.

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.9+
- MongoDB Veritabanı

### Yerel Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Ortam değişkenlerini ayarlayın (veya kod içinde düzenleyin):
   - `TOKEN`: Telegram Bot Token
   - `MONGO_URI`: MongoDB Bağlantı Adresi

3. Botu başlatın:
   ```bash
   python bot.py
   ```

## Render Üzerinde Kurulum

Bu bot, Render üzerinde **Web Service** olarak çalışacak şekilde yapılandırılmıştır.

1. Render'da yeni bir Web Service oluşturun.
2. GitHub reponuzu bağlayın.
3. **Environment Variables** kısmına şunları ekleyin:
   - `TOKEN`: Telegram Bot Token
   - `MONGO_URI`: MongoDB Bağlantı Adresi
   - `PYTHON_VERSION`: 3.10.0 (Önerilen)
4. Deploy edin!

## Nasıl Çalışır?

Bot, günlük burç verilerini [AIstrolog](https://github.com/kocerayk/AIstrolog) GitHub deposundan JSON formatında çeker ve işleyerek size sunar. Arka planda çalışan Flask sunucusu sayesinde Render gibi platformlarda uyku moduna girmeden çalışabilir.

## Komutlar

- `/start`: Botu başlatır ve ana menüyü gösterir.
- `/stop`: Günlük bildirim aboneliğinden çıkar.
