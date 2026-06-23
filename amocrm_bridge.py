from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
# O'zgartirmang, bular sizning ma'lumotlaringiz
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 
TEST_MOBILE_NUMBER = "+998975960976" 
# ==========================================================

def trigger_telephony_call(customer_phone):
    """
    onlinePBX orqali qo'ng'iroqni boshlash funksiyasi.
    Ushbu URL va format onlinePBX uchun standart hisoblanadi.
    """
    # Eng muhim qism: To'g'ri API manzili
    url = f"https://{DOMAIN}/api/v1/user/callback.json"
    
    # Ma'lumotlarni yuborish formati
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
        
        # onlinePBX ma'lumotlarni 'data' (form-data) ko'rinishida qabul qiladi
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        
        print(f"[TELEFONIYA] Status kodi: {response.status_code}")
        print(f"[TELEFONIYA] Server javobi: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"[TELEFONIYA] Texnik xatolik: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "AmoCRM-onlinePBX Bot ishlayapti!"}

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n" + "="*50)
    print(f"🔔 {datetime.now().strftime('%H:%M:%S')} - AmoCRM'DAN SIGNAL KELDI!")
    
    # Kelgan webhook ma'lumotlarini o'qish
    try:
        form_data = await request.form()
        data = dict(form_data)
        
        # Logda barcha kelgan ma'lumotlarni ko'rish (debug uchun)
        print("Mijoz ma'lumotlari:")
        for key, value in data.items():
            print(f" - {key}: {value}")
        
        # Test uchun: Har qanday webhook kelganda ko'rsatilgan test raqamiga tel qiladi
        # Real holatda data ichidan telefon raqamni ajratib olish mumkin
        success = trigger_telephony_call(TEST_MOBILE_NUMBER)
        
        if success:
            print("✅ Qo'ng'iroq muvaffaqiyatli boshlandi!")
        else:
            print("❌ Qo'ng'iroqni boshlab bo'lmadi.")

    except Exception as e:
        print(f"❌ Webhookni ishlashda xatolik: {e}")
    
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    # Render uchun port sozlamasi
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Server {port}-portda ishga tushmoqda...")
    uvicorn.run(app, host="0.0.0.0", port=port)