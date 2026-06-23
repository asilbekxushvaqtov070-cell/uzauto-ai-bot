from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"  # Sizning SIP telefoningiz (MicroSIP/Apparat)
TEST_MOBILE_NUMBER = "998975960976" # + belgisiz yozildi
# ==========================================================

def trigger_telephony_call(customer_phone):
    """
    onlinePBX orqali qo'ng'iroqni boshlash funksiyasi.
    """
    # URL manzili (Sizning domeningiz orqali)
    url = f"https://{DOMAIN}/api/v1/user/callback.json"
    
    # Raqamni faqat raqamlardan iborat holatga keltiramiz (+ belgisini olib tashlaydi)
    clean_phone = "".join(filter(str.isdigit, customer_phone))
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": clean_phone
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "AmoCRM-Bot-v2"
    }
    
    try:
        print(f"\n[SISTEMA] Qo'ng'iroq buyrug'i yuborilmoqda: {OPERATOR_EXTENSION} -> {clean_phone}")
        
        # onlinePBX-ga so'rov yuboramiz
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        
        print(f"[SISTEMA] HTTP Status: {response.status_code}")
        
        # onlinePBX-dan kelgan haqiqiy javobni tahlil qilamiz
        try:
            result = response.json()
            print(f"[SISTEMA] onlinePBX javobi: {result}")
            
            if result.get("status") == "success":
                print("✅ MUVAFFAQIYATLI: onlinePBX qo'ng'iroqni qabul qildi.")
                return True
            else:
                print(f"❌ XATOLIK: onlinePBX rad etdi. Sabab: {result.get('comment') or result.get('data')}")
                return False
        except:
            print(f"[SISTEMA] JSON bo'lmagan javob keldi: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEXNIK XATOLIK: {e}")
        return False

@app.get("/")
async def root():
    return {"status": "online", "message": "Bot muvaffaqiyatli ishlayapti"}

@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n" + "="*50)
    print(f"🔔 WEBHOOK QABUL QILINDI: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        form_data = await request.form()
        data = dict(form_data)
        
        # AmoCRM'dan kelgan ma'lumotlarni logga chiqaramiz
        print(f"Mijoz ma'lumotlari: {data}")
        
        # Qo'ng'iroqni boshlash
        # TEST_MOBILE_NUMBER o'rniga data ichidan kelgan raqamni ham qo'yish mumkin
        trigger_telephony_call(TEST_MOBILE_NUMBER)
        
    except Exception as e:
        print(f"❌ Webhook xatosi: {e}")
        
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)