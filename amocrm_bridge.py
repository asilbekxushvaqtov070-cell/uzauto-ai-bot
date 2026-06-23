from fastapi import FastAPI, Request
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100" # BU MUHIM: Bu extension OnlinePBX-da online bo'lishi kerak!

def trigger_telephony_call(customer_phone):
    # OnlinePBX plyus (+) belgisiz, faqat raqamlarni qabul qiladi
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"DEBUG: OnlinePBX-ga so'rov yuborilyapti: Kimdan: {OPERATOR_EXTENSION} -> Kimga: {clean_phone}")
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        # OnlinePBX qaytargan haqiqiy javobni ko'ramiz
        print(f"DEBUG: OnlinePBX javobi: Status {response.status_code}, Text: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"DEBUG: OnlinePBX-ga ulanishda XATO: {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    # 1. Kelayotgan ma'lumotni formatini olish
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n" + "="*30)
    print("YANGI WEBHOOK KELDI!")
    
    customer_phone = None

    # 2. AmoCRM-dan kelayotgan murakkab massiv ichidan raqamni topish
    # AmoCRM raqamni odatda 'leads[add][0][custom_fields][...][values][0][value]' ko'rinishida yuboradi
    # Biz hamma qiymatlarni tekshirib, raqamga o'xshashini qidiramiz
    for key, value in data.items():
        # Qiymatni faqat raqam qilib ko'ramiz
        potential_phone = re.sub(r'\D', '', str(value))
        # Agar raqam 9 tadan ko'p bo'lsa (masalan 998901234567) demak bu telefon raqami
        if len(potential_phone) >= 9 and potential_phone.startswith(('998', '7', '9')):
            customer_phone = potential_phone
            print(f"DEBUG: Raqam topildi: {key} -> {customer_phone}")
            break
            
    if not customer_phone:
        print("DEBUG: Webhook ichidan raqam topilmadi, test raqamiga tel qilinadi.")
        customer_phone = "998975960976"

    # 3. Qo'ng'iroqni ishga tushirish
    success = trigger_telephony_call(customer_phone)
    
    if success:
        print("NATIJA: Qo'ng'iroq buyrug'i muvaffaqiyatli yuborildi.")
        return {"status": "success", "phone": customer_phone}
    else:
        print("NATIJA: OnlinePBX buyruqni qabul qilmadi.")
        return {"status": "error", "message": "Call failed"}, 200 # AmoCRM-ga 200 qaytaramizki qayta-qayta yubormasin

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)