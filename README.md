# AIstrolog Bot 🌙

Bu proje, **AIstrolog** projesinden günlük burç yorumlarını çeken ve Telegram üzerinden kullanıcılara sunan bir bottur.

## Özellikler

- **Günlük Burç Yorumları:** Her gün güncellenen burç yorumlarını takip edebilirsiniz.
- **Kategoriler:** Genel, Aşk, Para ve Sağlık kategorilerinde özel yorumlar.
- **Günlük Bildirimler:** Her gün saat 12:00'de otomatik bildirim.
- **Web Entegrasyonu:** AIstrolog web sitesine hızlı erişim.

## Kurulum ve Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Botu başlatın:
   ```bash
   python bot.py
   ```

## Nasıl Çalışır?

Bot, günlük burç verilerini [AIstrolog](https://github.com/kocerayk/AIstrolog) GitHub deposundan JSON formatında çeker ve işleyerek size sunar.

## Komutlar

- `/start`: Botu başlatır ve ana menüyü gösterir.
- `/stop`: Günlük bildirim aboneliğinden çıkar.
