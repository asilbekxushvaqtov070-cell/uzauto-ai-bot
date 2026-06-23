from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import requests
import os
import re

app = FastAPI()

# ================= SOZLAMALAR =================
# 1. onlinePBX sozlamalari
PBX_DOMAIN = "pbx25683.onpbx.ru"
PBX_API_KEY = "RHRLb1c3dlpCZENiR2VnM2FXZFVQR0dsOUV6MGtjeTU"
OPERATOR_EXTENSION = "100"

# 2. AmoCRM sozlamalari
AMO_DOMAIN = "uzautotrailer" # amocrm.ru qismini yozmang
# BU YERGA AMO CRM DAN OLGAN UZUN TOKENNI QO'YING:
AMO_ACCESS_TOKEN = "SIZNING_AMOCRM_LONG_LIVED_TOKENINGIZ" 

# ================= FUNKSIYALAR =================

def clean_phone(phone_str):
    """Telefon raqamidagi ortiqcha belgilarni tozalaydi"""
    return re.sub(r'\D', '', str(phone_str))

def get_phone_from_amo(lead_id):
    """AmoCRM API orqali sdelkaga bog'langan mijoz raqamini oladi"""
    headers = {
        "Authorization": f"Bearer {AMO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Sdelkaga bog'langan kontaktni topamiz
    lead_url = f"https://{AMO_DOMAIN}.amocrm.ru/api/v4/leads/{lead_id}?with=contacts"
    
    try:
        res = requests.get(lead_url, headers=headers)
        if res.status_code != 200:
            print(f"❌ AmoCRM Lead topilmadi: {res.status_code}")
            return None
        
        lead_data = res.json()
        contacts = lead_data.get("_embedded", {}).get("contacts", [])
        if not contacts:
            print("❌ Sdelkaga bog'langan kontakt yo'q")
            return None
            
        contact_id = contacts[0].get("id")
        
        # 2. Kontaktning telefon raqamini olamiz
        contact_url = f"https://{AMO_DOMAIN}.amocrm.ru/api/v4/contacts/{contact_id}"
        res_contact = requests.get(contact_url, headers=headers)
        contact_data = res_contact.json()
        
        custom_fields = contact_data.get("custom_fields_values", [])
        if not custom_fields:
            return None
            
        for field in custom_fields:
            if field.get("field_code") == "PHONE":
                return field["values"][0]["value"]
                
    except Exception as e:
        print(f"❌ AmoCRM API bilan ishlashda xato: {e}")
    return None

def trigger_pbx_call(customer_phone):
    """onlinePBX orqali qo'ng'iroqni boshlaydi"""
    url = f"https://{PBX_DOMAIN}/api/v1/user/callback.json"
    payload = {
        "auth_key": PBX_API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone(customer_phone)
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"📡 onlinePBX status: {response.status_code}, Javob: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ onlinePBX ulanish xatosi: {e}")
        return False

# ================= WEBHOOK QABUL QILUVCHI =================

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    data = dict(form_data)
    
    print("\n🔔 AmoCRM'dan yangi webhook keldi!")
    
    # Webhook ichidan Lead ID ni ajratib olish (status o'zgarganda)
    # data strukturasidan ID ni qidiramiz
    lead_id = None
    if 'leads[status][0][id]' in data:
        lead_id = data['leads[status][0][id]']
    elif 'leads[update][0][id]' in data:
        lead_id = data['leads[update][0][id]']
    elif 'leads[add][0][id]' in data:
        lead_id = data['leads[add][0][id]']

    if lead_id:
        print(f"🆔 Lead ID: {lead_id}. Mijoz raqami qidirilmoqda...")
        # Mijoz raqamini olish va tel qilishni fonda bajaramiz (AmoCRM kutib qolmasligi uchun)
        background_tasks.add_task(process_call, lead_id)
    else:
        print("⚠️ Webhookda Lead ID topilmadi.")
        
    return {"status": "received"}

def process_call(lead_id):
    """Mijoz raqamini topib, qo'ng'iroqni amalga oshirish zanjiri"""
    customer_phone = get_phone_from_amo(lead_id)
    
    if customer_phone:
        print(f"📞 Mijoz raqami topildi: {customer_phone}. Qo'ng'iroq boshlanmoqda...")
        trigger_pbx_call(customer_phone)
    else:
        print(f"❌ Lead {lead_id} uchun telefon raqami topilmadi.")

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)