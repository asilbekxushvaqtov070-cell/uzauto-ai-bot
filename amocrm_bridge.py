from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= SOZLAMALAR =================
# onlinePBX ma'lumotlari
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"

# AmoCRM ma'lumotlari (Siz hozirgina olgan kalitlar)
AMO_CLIENT_ID = "cb8ecb39-a8d5-463d-982b-e8a7b1c075e7"
AMO_CLIENT_SECRET = "XNMFTfoi0LOIzikSIbnGGbnkuuxETUmyl3WQD1Kaku5SEjmoHJTOysyBfIOscRHd"
# ==============================================

def trigger_telephony_call(customer_phone):
    """onlinePBX orqali qo'ng'iroq qilish"""
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"📡 onlinePBX status: {response.status_code}")
        print(f"📝 Javob: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Qo'ng'iroqda xatolik: {e}")
        return False

@app.get("/")
async def home():
    return {"status": "Bot ishlamoqda", "integration": "AmoCRM + onlinePBX"}

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n" + "="*50)
    print(f"🔔 Webhook keldi: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # AmoCRM ma'lumotlarini qabul qilish
        form_data = await request.form()
        data = dict(form_data)
        
        # Logda ma'lumotlarni ko'rish
        print(f"Kelgan ma'lumot: {data}")

        # TEST: Webhook kelishi bilan ko'rsatilgan raqamga tel qiladi
        # (Xohlasangiz bu yerga o'z raqamingizni yozing)
        target_phone = "+998975960976" 
        
        success = trigger_telephony_call(target_phone)
        if success:
            print("✅ Qo'ng'iroq muvaffaqiyatli amalga oshirildi")
        else:
            print("❌ Qo'ng'iroq o'xshama-di")

    except Exception as e:
        print(f"❌ Webhook xatosi: {e}")
    
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)