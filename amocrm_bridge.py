from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" 
# ==============================================

def trigger_telephony_call(customer_phone):
    # 1. Raqamni faqat raqamlardan iborat qilish
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    # O'zbekiston raqami bo'lsa va 998 bo'lmasa, qo'shib qo'yamiz
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone

    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"--- OnlinePBX ga so'rov: Kimga: {clean_phone} ---")
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        res_json = response.json()
        print(f"OnlinePBX Javobi: {res_json}")
        
        if res_json.get('status') == 'error':
            error_msg = res_json.get('data', 'Nomaalum xato')
            if error_msg == 'from_not_online':
                print(f"XATO: {OPERATOR_EXTENSION}-ichki raqamli operator hozir ONLINE emas!")
            elif error_msg == 'auth_key_wrong':
                print("XATO: OnlinePBX API kaliti xato!")
        return True
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    # AmoCRM ma'lumotlarini olish
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n" + "="*30)
    print("WEBHOOK KELDI")
    
    customer_phone = None

    # AmoCRM webhookda raqamni qidirish (murakkab kalitlar ichidan)
    for key, value in data.items():
        # Raqamga o'xshash qiymatni qidiramiz (kamida 9 ta raqam bo'lsa)
        val_str = str(value)
        clean_val = re.sub(r'\D', '', val_str)
        if len(clean_val) >= 9:
            customer_phone = clean_val
            print(f"Raqam topildi: {customer_phone}")
            break
            
    if not customer_phone:
        print("Webhook ichidan raqam topilmadi, test raqami ishlatiladi.")
        customer_phone = "998975960976"

    # Qo'ng'iroqni fonda ishga tushiramiz (server o'chib qolmasligi uchun)
    background_tasks.add_task(trigger_telephony_call, customer_phone)
    
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)