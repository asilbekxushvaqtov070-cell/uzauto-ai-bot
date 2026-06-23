from fastapi import FastAPI, Request
import requests # type: ignore
import re

app = FastAPI()

ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    
    # Kelgan ma'lumotni logda ko'rish uchun (FastAPI/Vercel uchun)
    print(f"DEBUG: AmoCRM-dan kelgan DATA: {data}")
    
    customer_phone = None
    for key, value in data.items():
        # Raqamni qidirish (qiymat ichida kamida 9 ta raqam bo'lsa)
        clean_val = re.sub(r'\D', '', str(value))
        if len(clean_val) >= 9:
            customer_phone = clean_val
            break
            
    if not customer_phone:
        customer_phone = "998975960976" # Test raqamingiz

    print(f"DEBUG: OnlinePBX-ga yuborilayotgan raqam: {customer_phone}")

    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    response = requests.post(url, data=payload)
    res_json = response.json()
    
    print(f"DEBUG: OnlinePBX javobi: {res_json}")
    
    return {"status": "ok", "sent_phone": customer_phone, "onlinepbx": res_json}

@app.get("/")
async def root():
    return {"message": "Server ishlayapti!"}