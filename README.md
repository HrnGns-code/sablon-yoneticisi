
# Şablon Yöneticisi (Windows)

Hazır metinleri kategorilere ayırıp tek tıkla **panoya kopyalayan** ve **aktif pencereye yapıştırabilen**, ayrıca **global klavye kısayolları** (ör. `Ctrl+Shift+T`) ile arka planda çalışan bir Windows masaüstü uygulaması.

## Özellikler
- Kategoriler (İptal, Şikayet, Özür vb.) altında **şablon metinleri** tutar.
- Uygulama içinden **yeni kategori/şablon ekleme, düzenleme, silme**.
- Şablona **çift tık** → panoya kopyalar ve **isteğe bağlı** hemen aktif pencereye yapıştırır.
- **Sağ tık** menüsünden “Ctrl+Shift+T / Ctrl+Shift+Q kısayoluna ata”.
- **Sistem tepsisine** küçülür, arka planda **global kısayolları** dinlemeye devam eder.
- Veriler `templates.json`, ayarlar `settings.json` (aynı klasörde).

## Kurulum
1. Windows’a Python 3.9+ kurulu olmalı.
2. Bu klasöre Komut İstemi (CMD) ile gelin ve bağımlılıkları kurun:
   ```bash
   pip install -r requirements.txt
   ```
   > Not: `keyboard` modülü Windows’ta **global kısayollar** için *yönetici izni* gerektirebilir. Gerekirse Komut İstemi’ni **Yönetici olarak çalıştırın**.

## Çalıştırma
```bash
python app.py
```

## Kullanım İpuçları
- **Şablon ekleme:** Sol listeden bir **kategori** seçin → sağ alttaki **“Şablon Ekle”**.
- **Şablonu kullanma:** Şablona **çift tıklayın** (panoya kopyalar ve ayara göre yapıştırır).
- **Sağ tık menüsü:** “Panoya kopyala”, “Aktif pencereye yapıştır”, “Kısayol ata”.
- **Kısayol atama:** Şablona sağ tıklayın → ör. “Ctrl+Shift+T kısayoluna ata”.
- **Otomatik yapıştırmayı kapatmak:** `settings.json` içindeki `"auto_paste_on_click": true` değerini `false` yapın.
- **Kapatınca tepsiye inme:** `settings.json` → `"minimize_to_tray_on_close"`.

## Sık Sorular
- **Kısayol çalışmıyor:** Kısayol başka program tarafından kullanılıyor olabilir veya `keyboard` için yönetici izni gerekebilir. Alternatif bir kombinasyon deneyin ya da CMD’yi yönetici olarak çalıştırın.
- **Panoya kopyalandı ama yapışmadı:** Bazı uygulamalar farklı kısayollar kullanabilir. `Ctrl+V` yerine uygulama içi menüden yapıştırmayı deneyin. Gerekirse şablona sağ tıklayıp “Aktif pencereye yapıştır” deyin.
- **Verileri taşımak:** `templates.json` dosyasını başka bir bilgisayara kopyalayın.

## Derleyip Tek Dosya EXE almak ister misiniz?
PyInstaller ile deneyebilirsiniz (opsiyonel):
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed app.py
```
EXE `dist/app.exe` altında oluşur. (Global kısayollar için yine yönetici izni gerekebilir.)
