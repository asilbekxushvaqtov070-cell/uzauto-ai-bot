from fastapi import FastAPI, Request
import requests # type: ignore
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 

def trigger_telephony_call(customer_phone):
    # Raqamni faqat raqamlardan iborat qilish
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    # O'zbekiston raqami formatini tekshirish
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone

    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    
    customer_phone = None
    # AmoCRM-dan raqamni qidirish
    for key, value in data.items():
        clean_val = re.sub(r'\D', '', str(value))
        if len(clean_val) >= 9:
            customer_phone = clean_val
            break
            
    if not customer_phone:
        customer_phone = "998975960976"

    # Qo'ng'iroqni amalga oshirish
    result = trigger_telephony_call(customer_phone)
    
    return {"status": "processed", "onlinepbx_response": result}

@app.get("/")
async def root():
    return {"message": "Server ishlayapti!"}