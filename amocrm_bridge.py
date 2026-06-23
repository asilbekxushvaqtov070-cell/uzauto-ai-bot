from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
# YANGI API KALIT O'RNATILDI
API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 
TEST_MOBILE_NUMBER = "+998975960976" 
# ==========================================================

def trigger_telephony_call(customer_phone):
    """
    onlinePBX orqali qo'ng'iroqni boshlash funksiyasi.
    """
    # To'g'ri API manzili
    url = f"https://{DOMAIN}/api/v1/user/callback.json"
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    headers = {
        "User-Agent": "AmoCRM-Bot-Integrator/1.0",
        "Accept": "application/json"
    }
    
    try:
        print(f"\n[TELEFONIYA] So'rov yuborilmoqda: {OPERATOR_EXTENSION} -> {customer_phone}")
        
        # Ma'lumotlarni yuborish
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        
        print(f"[TELEFONIYA] Status kodi: {response.status_code}")
        print(f"[TELEFONIYA] Server javobi: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ onlinePBX xato qaytardi: {response.text}")
            return False
            
    except Exception as e:
        print(f"[TELEFONIYA] Texnik xatolik: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "AmoCRM-onlinePBX Bot ishlayapti!", "status": "active"}

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n" + "="*50)
    print(f"🔔 {datetime.now().strftime('%H:%M:%S')} - AmoCRM'DAN SIGNAL KELDI!")
    
    try:
        form_data = await request.form()
        data = dict(form_data)
        
        # Logda kelgan ma'lumotlarni ko'rsatish
        print("Mijoz ma'lumotlari tahlili:")
        for key, value in data.items():
            print(f" - {key}: {value}")
        
        # Qo'ng'iroqni amalga oshirish
        # DIQQAT: Hozir test uchun faqat TEST_MOBILE_NUMBER ga tel qiladi.
        # Agar mijozga tel qilmoqchi bo'lsangiz, raqamni 'data' ichidan olish kerak.
        success = trigger_telephony_call(TEST_MOBILE_NUMBER)
        
        if success:
            print("✅ Qo'ng'iroq muvaffaqiyatli buyurtma qilindi!")
        else:
            print("❌ Qo'ng'iroq buyurtmasida xato.")

    except Exception as e:
        print(f"❌ Webhookni ishlashda xatolik: {e}")
    
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    # Render uchun port
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Bot {port}-portda ishga tushmoqda...")
    uvicorn.run(app, host="0.0.0.0", port=port)