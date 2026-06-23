from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
# Diqqat: API_KEY maxfiy qolishi kerak. 
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
OPERATOR_EXTENSION = "100"  # Sizning ichki SIP raqamingiz
TEST_MOBILE_NUMBER = "+998975960976" 
# ==========================================================

def trigger_telephony_call(customer_phone):
    """
    onlinePBX orqali qo'ng'iroqni boshlash funksiyasi.
    To'g'ri API manzili: https://api.onlinepbx.ru/api/v1/user/callback.json
    """
    # TO'G'IRLANGAN URL:
    url = "https://api.onlinepbx.ru/api/v1/user/callback.json"
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        print(f"📞 Telefoniya qo'ng'iroqni boshlamoqda: {OPERATOR_EXTENSION} ➡️ {customer_phone}")
        
        # onlinePBX ma'lumotlarni form-data ko'rinishida qabul qiladi
        response = requests.post(url, data=payload, headers=headers)
        
        print(f"📡 Server holati (Status Code): {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("☎️ onlinePBX javobi:", result)
            except:
                print("☎️ onlinePBX javob qaytardi, lekin JSON formatida emas:", response.text)
        else:
            print(f"❌ Xato yuz berdi. Server javobi: {response.text}")
            
    except Exception as e:
        print(f"❌ Telefoniya bilan ulanishda texnik xatolik: {e}")

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n================================================")
    print("🔔 AmoCRM'DAN YANGI SIGNAL KELDI!")
    
    # Kelgan ma'lumotlarni olish
    form_data = await request.form()
    data = dict(form_data)
    
    # Logda barcha kelgan ma'lumotlarni ko'rish
    for key, value in data.items():
        print(f"{key}: {value}")
         
    # Qo'ng'iroqni amalga oshirish
    # Real loyihada TEST_MOBILE_NUMBER o'rniga data ichidan kelgan telefon raqamni qo'yish kerak
    trigger_telephony_call(TEST_MOBILE_NUMBER)
         
    print("================================================\n")
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Bot {port}-portda ishga tushmoqda...")
    uvicorn.run(app, host="0.0.0.0", port=port) 