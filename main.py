from fastapi import FastAPI, Request, BackgroundTasks
import requests
import re

app = FastAPI()

ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 

def make_call(phone):
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {"auth_key": ONLINEPBX_API_KEY, "from": OPERATOR_EXTENSION, "to": phone}
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"OnlinePBX natijasi: {r.text}")
    except Exception as e:
        print(f"OnlinePBX xatosi: {e}")

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    # Ma'lumotlarni olish
    body = await request.form()
    data = dict(body)
    print(f"Webhook keldi: {data}")

    customer_phone = None
    for key, value in data.items():
        clean_val = re.sub(r'\D', '', str(value))
        if len(clean_val) >= 9:
            customer_phone = clean_val
            break

    if customer_phone:
        # Qo'ng'iroqni "fonda" (background) yuboramiz, 
        # shunda Vercel AmoCRM-ga tezroq javob qaytaradi
        background_tasks.add_task(make_call, customer_phone)
        return {"status": "started", "phone": customer_phone}
    
    return {"status": "no_phone_found"}

@app.get("/")
async def root():
    return {"message": "Server ishlayapti!"}