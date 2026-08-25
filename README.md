# Yahoo Finance Quote API

Yahoo Finance'tan fiyat ve temel istatistikleri çekip JSON olarak döndüren basit bir FastAPI uygulaması.

## Yerelde çalıştırma

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Ardından örnek endpoint'i açın:

```text
http://127.0.0.1:8000/quote/NVDA
```

Başarılı yanıt örneği:

```json
{
  "ticker": "NVDA",
  "price": "208.48",
  "stats": {
    "Previous Close": "214.72",
    "Open": "215.38"
  }
}
```

Yahoo isteği engellerse, zaman aşımına uğrarsa veya sayfa parse edilemezse API `200` yerine uygun bir hata durum kodu ve şu biçimde JSON döndürür:

```json
{"error": "Hata açıklaması"}
```

## Render'a deploy

1. Projeyi bir GitHub deposuna gönderin.
2. Render panelinde **New +** > **Web Service** seçin.
3. GitHub deponuzu bağlayın.
4. Runtime olarak **Python 3** seçin.
5. Build Command alanına şunu yazın:

   ```text
   pip install -r requirements.txt
   ```

6. Start Command alanına şunu yazın:

   ```text
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

7. **Create Web Service** düğmesine basın.

Deploy tamamlandıktan sonra endpoint şu biçimde kullanılabilir:

```text
https://uygulama-adiniz.onrender.com/quote/NVDA
```
