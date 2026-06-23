from fastapi import FastAPI, Request
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"

def trigger_telephony_call(customer_phone):
    # 1. Raqamni tozalash: faqat raqamlarni qoldiramiz (+ belgisini olib tashlaymiz)
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"DEBUG: OnlinePBX ga so'rov yuborilmoqda: {clean_phone}")
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"DEBUG: OnlinePBX javobi: Status: {response.status_code}, Body: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"XATOLIK (OnlinePBX): {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    # AmoCRM ma'lumotlarini olish
    form_data = await request.form()
    data = dict(form_data)
    
    # 1. KELAYOTGAN MA'LUMOTNI KONSOLDA KO'RISH (Juda muhim!)
    print("--- YANGI WEBHOOK KELDI ---")
    # print(data) # Agar ma'lumotni to'liq ko'rmoqchi bo'lsangiz buni yoqing
    
    customer_phone = None

    # 2. AmoCRM dan telefon raqamini qidirish (murakkabroq qidiruv)
    # AmoCRM webhookda telefon raqami odatda value ichida keladi
    for key, value in data.items():
        # Agar qiymat telefon raqamiga o'xshasa (kamida 7 ta raqam bo'lsa)
        clean_val = re.sub(r'\D', '', str(value))
        if len(clean_val) >= 9 and ("phone" in key.lower() or "value" in key.lower()):
            customer_phone = clean_val
            break
            
    if not customer_phone:
        print("DIQQAT: Webhook ichidan telefon raqami topilmadi, test raqami ishlatiladi.")
        customer_phone = "998975960976"

    # 3. Qo'ng'iroqni boshlash
    success = trigger_telephony_call(customer_phone)
    
    if success:
        return {"status": "success", "phone": customer_phone}
    else:
        return {"status": "error", "message": "Call failed"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)