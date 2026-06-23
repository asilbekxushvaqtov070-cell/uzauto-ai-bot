from fastapi import FastAPI, Request
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
ONLINEPBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
ONLINEPBX_DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"  # DIQQAT: Bu operator OnlinePBX panelida "Online" (yashil) bo'lishi shart!

def trigger_telephony_call(customer_phone):
    # 1. Raqamni faqat raqamlardan iborat holatga keltirish (plyus va boshqa belgilarsiz)
    clean_phone = re.sub(r'\D', '', str(customer_phone))
    
    # Agar raqam 998 bilan boshlanmasa va 9 ta raqam bo'lsa, 998 qo'shamiz (O'zbekiston uchun)
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone

    url = f"https://{ONLINEPBX_DOMAIN}/api/v1/user/callback.json"
    
    payload = {
        "auth_key": ONLINEPBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    print(f"DEBUG: OnlinePBX-ga so'rov yuborilmoqda. Kimga: {clean_phone}")
    
    try:
        # OnlinePBX API ba'zan form-data emas, JSON kutishi mumkin. 
        # Shuning uchun 'data=' o'rniga 'json=' ishlatib ko'rish ham mumkin.
        response = requests.post(url, data=payload, timeout=10)
        
        # Terminalda OnlinePBX aynan nima deb javob berayotganini ko'ramiz
        print(f"DEBUG: OnlinePBX javob kodi: {response.status_code}")
        print(f"DEBUG: OnlinePBX javob matni: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"XATOLIK: OnlinePBX-ga ulanib bo'lmadi: {e}")
        return False

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    # AmoCRM ma'lumotlarini olish
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n" + "="*40)
    print("YANGI WEBHOOK KELDI!")
    
    customer_phone = None

    # Raqamni qidirish: AmoCRM webhookda raqam odatda "value" yoki "phone" kalitlarida keladi
    for key, value in data.items():
        val_str = str(value)
        # Agar qiymat ichida kamida 9 ta raqam bo'lsa, bu telefon deb hisoblaymiz
        clean_val = re.sub(r'\D', '', val_str)
        if len(clean_val) >= 9:
            customer_phone = clean_val
            print(f"DEBUG: Raqam topildi: {customer_phone}")
            break
            
    if not customer_phone:
        print("DEBUG: Webhook ichida raqam topilmadi, test raqami ishlatiladi.")
        customer_phone = "998975960976"

    # Qo'ng'iroqni amalga oshirish
    success = trigger_telephony_call(customer_phone)
    
    if success:
        return {"status": "success", "phone": customer_phone}
    else:
        # Qo'ng'iroq o'xshamasa ham 200 qaytaramiz, aks holda AmoCRM qayta-qayta webhook yuboraveradi
        return {"status": "failed", "reason": "OnlinePBX error"}, 200

if __name__ == "__main__":
    # Render yoki boshqa hostinglar uchun PORT sozlamasi
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)