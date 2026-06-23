from fastapi import FastAPI, Request
import uvicorn
import requests
import os

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"

# AmoCRM-dan ma'lumot olish uchun (Siz yuborgan token)
# Tokenlar vaqt o'tishi bilan eskiradi, shuning uchun shunchaki avtomat tel qilishni qoldiramiz.
# ==============================================

def trigger_telephony_call(customer_phone):
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    
    # AmoCRM webhook orqali ko'pincha telefon raqamini ham yuboradi.
    # Agar telefon raqami webhook ichida bo'lsa, uni olamiz:
    
    customer_phone = None
    
    # AmoCRM-dan kelishi mumkin bo'lgan har xil formatlarni tekshiramiz
    for key, value in data.items():
        if "phone" in key.lower() or "contacts[id]" in key.lower():
            # Agar raqam webhook ichida bo'lsa (sozlangan bo'lsa)
            customer_phone = value 
            break
            
    if not customer_phone:
        # Agar mijoz raqami topilmasa, test raqamingizga tel qiladi
        customer_phone = "+998975960976"

    print(f"📞 Mijozga qo'ng'iroq qilinmoqda: {customer_phone}")
    trigger_telephony_call(customer_phone)
    
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)