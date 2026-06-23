from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
DOMAIN = "pbx25683.onpbx.ru"  # Sizning shaxsiy domeningiz
OPERATOR_EXTENSION = "100"    # Ichki raqam
TEST_MOBILE_NUMBER = "+998975960976" 
# ==========================================================

def trigger_telephony_call(customer_phone):
    """
    onlinePBX qo'ng'iroqni boshlash (Click-to-call).
    Shaxsiy domen orqali murojaat qilamiz.
    """
    # Shaxsiy domen orqali API manzili
    url = f"https://{DOMAIN}/api/v1/user/callback.json"
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    # Headers qismiga Content-Type qo'shish muhim
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "AmoCRM-Bot/1.0"
    }
    
    try:
        print(f"📞 Qo'ng'iroq buyrug'i yuborilmoqda: {OPERATOR_EXTENSION} -> {customer_phone}")
        print(f"🔗 Manzil: {url}")
        
        # onlinePBX ma'lumotlarni form-data ko'rinishida kutadi
        response = requests.post(url, data=payload, headers=headers)
        
        print(f"📡 Server holati: {response.status_code}")
        
        if response.status_code == 200:
            print("☎️ Muvaffaqiyatli: onlinePBX so'rovni qabul qildi.")
            print("Javob:", response.text)
        else:
            print(f"❌ Xato! Server javobi: {response.text}")
            
    except Exception as e:
        print(f"❌ Texnik xatolik: {e}")

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n" + "="*50)
    print("🔔 AmoCRM Webhook qabul qilindi")
    
    form_data = await request.form()
    data = dict(form_data)
    
    # Kelgan ma'lumotlarni logga yozish (ixtiyoriy)
    # print(f"Ma'lumot: {data}")
    
    # Qo'ng'iroqni boshlash
    trigger_telephony_call(TEST_MOBILE_NUMBER)
    
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)