from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from datetime import datetime

app = FastAPI()

# ================= TELEFONIYA SOZLAMALARI =================
API_KEY = "TWNsZVMzZGJkM2JLV1lRU2ZsdHRYNVlCOGZzdUJsVzg"
DOMAIN = "pbx25683.onpbx.ru"
OPERATOR_EXTENSION = "100"  # Sizning ichki SIP raqamingiz
TEST_MOBILE_NUMBER = "+998975960976"  # Sizning mobil raqamingiz (Nodir aka)
# ==========================================================

# onlinePBX orqali qo'ng'iroqni boshlash funksiyasi
def trigger_telephony_call(customer_phone):
    # onlinePBX rasmiy barqaror V1 API manzili
    url = "https://api.onlinepbx.ru/v1/callback/originate.json"
    
    payload = {
        "auth_key": API_KEY,
        "from": OPERATOR_EXTENSION,
        "to": customer_phone
    }
    
    # Server bizni robot deb o'ylab bloklamasligi uchun unga brauzer niqobini kiygizamiz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"📞 Telefoniya qo'ng'iroqni boshlamoqda: {OPERATOR_EXTENSION} ➡️ {customer_phone}")
        response = requests.post(url, data=payload, headers=headers)
        
        print("Status Code:", response.status_code)
        print("Server qaytargan xom matn:", response.text)
        
        if response.status_code == 200:
            result = response.json()
            print("☎️ onlinePBX serveridan kelgan javob:", result)
        else:
            print("❌ onlinePBX xato qaytardi (Server javobi 200 emas).")
            
    except Exception as e:
        print("❌ Telefoniya bilan ulanishda xatolik yuz berdi:", e)

# AmoCRM'dan keladigan signalni (Webhook) qabul qiluvchi manzil
@app.post("/amocrm-webhook")
async def receive_webhook(request: Request):
    print("\n================================================")
    print("🔔 AmoCRM'DAN YANGI SIGNAL KELDI!")
    print("================================================")
    
    # Kelgan form-ma'lumotlarni o'qiymiz
    form_data = await request.form()
    data = dict(form_data)
    
    hozirgi_vaqt = datetime.now().strftime('%H:%M:%S')
    print("Mijoz ma'lumotlari tahlili:")
    for kalit, qiymat in data.items():
         print(f"{kalit}: {qiymat}")
         
    # Test rejimida sizning raqamingizga qo'ng'iroq qiladi
    trigger_telephony_call(TEST_MOBILE_NUMBER)
         
    print("================================================\n")
    return {"status": "success"}

if __name__ == "__main__":
    # Onlayn server beradigan portni avtomatik aniqlaymiz (Render uchun muhim)
    port = int(os.environ.get("PORT", 8000))
    print(f"AmoCRM ulanish serveri {port}-portda ishga tushmoqda...")
    uvicorn.run(app, host="0.0.0.0", port=port)