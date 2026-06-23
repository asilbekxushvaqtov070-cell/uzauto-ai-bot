from fastapi import FastAPI, Request
import requests
import re
import json

app = FastAPI()

ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    try:
        # AmoCRM-dan kelayotgan ma'lumotni olish
        form_data = await request.form()
        data = dict(form_data)
        print(f"DEBUG: Kelgan ma'lumot: {data}")
        
        customer_phone = None
        # Raqamni qidirish
        for key, value in data.items():
            clean_val = re.sub(r'\D', '', str(value))
            if len(clean_val) >= 9:
                customer_phone = clean_val
                break
        
        if not customer_phone:
            customer_phone = "998975960976"

        # OnlinePBX-ga so'rov
        url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
        payload = {
            "auth_key": ONLINEPBX_API_KEY,
            "from": OPERATOR_EXTENSION,
            "to": customer_phone
        }
        
        print(f"DEBUG: OnlinePBX-ga yuborilmoqda: {customer_phone}")
        
        response = requests.post(url, data=payload, timeout=15)
        
        # JAVOBNI TEKSHIRISH (500 xato bermasligi uchun)
        try:
            res_json = response.json()
        except:
            res_json = response.text

        print(f"DEBUG: OnlinePBX-dan javob: {res_json}")
        
        return {"status": "ok", "onlinepbx": res_json}

    except Exception as e:
        # Agar kodda xato bo'lsa, 500 o'rniga xatoni ko'rsatadi
        print(f"KRITIK XATO: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "Server ishlayapti!"}