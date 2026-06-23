from fastapi import FastAPI, Request, BackgroundTasks
import requests
import re

app = FastAPI()

# SOZLAMALAR
API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR = "100"

def make_call(customer_phone):
    """OnlinePBX-ga qo'ng'iroq buyrug'ini yuborish"""
    # Raqamni faqat raqamlardan iborat qilish
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone
    
    url = f"https://{DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR,
        "to": clean_phone
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"OnlinePBX Natijasi: {r.text}")
    except Exception as e:
        print(f"Ulanishda xato: {e}")

@app.post("/amocrm-webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        # 1. AmoCRM-dan kelgan ma'lumotni o'qish
        body = await request.form()
        data = dict(body)
        
        customer_phone = None
        # 2. Ma'lumotlar ichidan telefon raqamini topish
        for key, value in data.items():
            val_str = str(value)
            clean_val = re.sub(r'\D', '', val_str)
            if len(clean_val) >= 9:
                customer_phone = clean_val
                break
        
        # Agar raqam topilmasa, test raqami
        if not customer_phone:
            customer_phone = "998975960976"

        # 3. Qo'ng'iroqni fonda ishga tushirish (Vercel qotib qolmasligi uchun)
        background_tasks.add_task(make_call, customer_phone)
        
        return {"status": "ok", "message": "Buyruq qabul qilindi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def status():
    return {"message": "Server ishlayapti!"}