from fastapi import FastAPI, Request
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"  # Operator SIP telefonda ONLINE bo'lishi shart!

def trigger_telephony_call(customer_phone):
    # Raqamni faqat raqamlardan iborat qilish (+ belgisiz)
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"\n[OnlinePBX] So'rov yuborilmoqda: {OPERATOR_EXTENSION} -> {clean_phone}")
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        # BU YERDA ONLINEPBX QAYTARGAN JAVOBNI KO'RAMIZ
        print(f"[OnlinePBX] Javob kodi: {response.status_code}")
        print(f"[OnlinePBX] Javob matni: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[OnlinePBX] Ulanishda xato: {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n" + "="*30)
    print("WEBHOOK QABUL QILINDI")
    
    customer_phone = None

    # AmoCRM ma'lumotlari ichidan telefon raqamini qidirish
    for key, value in data.items():
        val_str = str(value)
        clean_val = re.sub(r'\D', '', val_str)
        if len(clean_val) >= 9 and any(p in key.lower() for p in ["phone", "value", "contact"]):
            customer_phone = clean_val
            print(f"Topilgan raqam: {customer_phone} (Kalit: {key})")
            break
            
    if not customer_phone:
        print("Mijoz raqami topilmadi, test raqam ishlatiladi.")
        customer_phone = "998975960976"

    # Qo'ng'iroqni boshlash
    trigger_telephony_call(customer_phone)
    
    return {"status": "received"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)