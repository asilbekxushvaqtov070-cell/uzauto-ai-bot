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
    # OnlinePBX faqat raqamlarni qabul qiladi, + belgisini olib tashlaymiz
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"DEBUG: OnlinePBX ga so'rov ketmoqda...")
    print(f"DEBUG: Operator: {OPERATOR_EXTENSION} -> Mijoz: {clean_phone}")
    
    try:
        # data=payload (form-urlencoded) shaklida yuboramiz
        response = requests.post(url, data=payload, timeout=15)
        print(f"DEBUG: OnlinePBX Status kodi: {response.status_code}")
        print(f"DEBUG: OnlinePBX Javob matni: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"DEBUG: OnlinePBX ulanishda xato: {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    # AmoCRM yuborgan barcha ma'lumotlarni o'qiymiz
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n" + "="*40)
    print("YANGI WEBHOOK KELDI!")
    
    customer_phone = None

    # Raqamni qidirish
    for key, value in data.items():
        val_str = str(value)
        clean_val = re.sub(r'\D', '', val_str)
        # Agar kamida 9 ta raqam bo'lsa, bu telefon raqami deb hisoblaymiz
        if len(clean_val) >= 9:
            customer_phone = clean_val
            print(f"DEBUG: Raqam webhook ichidan topildi: {customer_phone}")
            break
            
    if not customer_phone:
        print("DEBUG: Webhook ichida raqam yo'q, test raqami ishlatiladi.")
        customer_phone = "998975960976"

    # Qo'ng'iroq qilish buyrug'ini yuboramiz
    trigger_telephony_call(customer_phone)
    
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)