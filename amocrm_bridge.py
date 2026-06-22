from fastapi import FastAPI, Request
import uvicorn
import requests

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"  # Sizning ichki SIP raqamingiz
TEST_MOBILE_NUMBER = "+998998118889"  # Sizning mobil raqamingiz (Nodir aka)
# ==========================================================

# onlinePBX orqali qo'ng'iroqni boshlash funksiyasi
def trigger_telephony_call(customer_phone):
    url = "https://api.onlinepbx.ru/v1/callback/originate.json"
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    # Server bizni bloklamasligi uchun o'zimizni Chrome brauzeri qilib ko'rsatamiz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"📞 Telefoniya qo'ng'iroqni boshlamoqda: {OPERATOR_EXTENSION} ➡️ {customer_phone}")
        response = requests.post(url, data=payload, headers=headers)
        
        print("Status Code:", response.status_code)
        print("Server qaytargan xom matn:", response.text)
        
        if response.status_code == 200:
            result = response.json()
            print("☎️ onlinePBX serveridan kelgan javob:", result)
        else:
            print("❌ onlinePBX xato qaytardi (Server javobi 200 emas).")
            
    except Exception as e:
        print("❌ Telefoniya bilan ulanishda xatolik yuz berdi:", e)

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n================================================")
    print("🔔 AmoCRM'DAN YANGI SIGNAL KELDI!")
    print("================================================")
    
    form_data = await request.form()
    data = dict(form_data)
    
    print("Mijoz ma'lumotlari tahlili:")
    for kalit, qiymat in data.items():
         print(f"{kalit}: {qiymat}")
         
    # Test rejimida sizga qo'ng'iroq qiladi
    trigger_telephony_call(TEST_MOBILE_NUMBER)
         
    print("================================================\n")
    return {"status": "success"}

if __name__ == "__main__":
    print("AmoCRM ulanish serveri ishga tushmoqda...")
    uvicorn.run(app, host="127.0.0.1", port=8000)