"""
╔══════════════════════════════════════════════════════╗
║       ZAKOVATBOT — CrewAI AGENT MODULI              ║
║                                                      ║
║  Bu fayl zakovatbot_full.py ga qo'shimcha!          ║
║  Har kecha avtomatik yangi savollar yaratadi!       ║
║                                                      ║
║  O'RNATISH:                                         ║
║  pip install crewai                                 ║
║                                                      ║
║  ISHGA TUSHIRISH:                                   ║
║  python zakovatbot_agent.py                         ║
╚══════════════════════════════════════════════════════╝
"""

import json
import os
import asyncio
import aiohttp
import schedule
import time
from datetime import datetime
from crewai import Agent, Task, Crew, Process

# ══════════════════════════════════════════
# ⚙️ SOZLAMALAR — zakovatbot_full.py dan
# ══════════════════════════════════════════
GROQ_API_KEY = "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"   # zakovatbot_full.py dagi key
BOT_TOKEN    = "8045205315:AAEaNAopNtbyFkZ97h7lDI3_hwl8pzWz9mg"       # zakovatbot_full.py dagi token
ADMIN_ID     =  1967786876                          # zakovatbot_full.py dagi admin id
DB_FILE      = "zakovatbot_db.json"        # bir xil fayl!

# ══════════════════════════════════════════
# 📚 MAVZULAR — Har fan uchun
# ══════════════════════════════════════════
MAVZULAR = {
    "Matematika": [
        "Kasrlar", "Foizlar", "Tenglama", "Geometrik shakllar",
        "Algebra", "Sonlar nazariyasi", "Logarifm", "Trigonometriya"
    ],
    "Tarix": [
        "Amir Temur", "Temuriylar", "Ipak yo'li", "Sohibqiron",
        "Mustaqillik", "Qadimgi davlatlar", "Buyuk allomalar",
        "Al-Xorazmiy", "Ibn Sino", "Beruniy"
    ],
    "Biologiya": [
        "Hujayralar", "O'simliklar", "Hayvonlar", "Inson tanasi",
        "Ekotizim", "Genetika", "Evolyutsiya", "Mikrobiologiya"
    ],
    "Geografiya": [
        "O'zbekiston viloyatlari", "Dunyo okeanlari", "Tog'lar",
        "Daryolar", "Iqlim", "Aholishunoslik", "Qit'alar"
    ],
    "Fizika": [
        "Mexanika", "Termodinamika", "Elektr", "Optika",
        "Magnit", "Yadro fizikasi", "Kvant fizikasi"
    ],
    "Kimyo": [
        "Davriy jadval", "Kimyoviy reaksiyalar", "Metallar",
        "Organik kimyo", "Oksidlanish", "Eritmalar"
    ],
    "Ingliz tili": [
        "Grammar", "Vocabulary", "Idioms",
        "Tenses", "Prepositions", "Phrasal verbs"
    ],
    "Informatika": [
        "Algoritm", "Python asoslari", "Ma'lumotlar bazasi",
        "Internet", "Dasturlash", "Sun'iy intellekt"
    ],
}

# Bugun qaysi fan navbatida?
def bugungi_fan() -> str:
    fanlar = list(MAVZULAR.keys())
    kun_raqami = datetime.now().timetuple().tm_yday
    return fanlar[kun_raqami % len(fanlar)]

def bugungi_mavzu(fan: str) -> str:
    mavzular = MAVZULAR.get(fan, ["Asosiy mavzu"])
    soat = datetime.now().hour
    return mavzular[soat % len(mavzular)]

# ══════════════════════════════════════════
# 🤖 CREWAI AGENTLAR
# ══════════════════════════════════════════

def agentlar_yaratish(fan: str, sinf: str, mavzu: str):

    # AGENT 1 — Tadqiqotchi
    tadqiqotchi = Agent(
        role="O'zbek ta'lim tadqiqotchisi",
        goal=f"{fan} fanidan {sinf}-sinf o'quvchilari uchun "
             f"{mavzu} mavzusida qiziqarli faktlar top",
        backstory=f"""Sen O'zbekistonning eng tajribali 
                    {fan} o'qituvchisisаn. 
                    20 yillik tajribang bor.
                    Bolalar sevadigan, qiziqarli 
                    faktlarni yaxshi bilasan.
                    O'zbek maktab dasturini mukammal bilasan.""",
        verbose=True,
        allow_delegation=False,
        llm_config={
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": GROQ_API_KEY,
        }
    )

    # AGENT 2 — Savol Yozuvchi
    savol_yozuvchi = Agent(
        role="Test savollari mutaxassisi",
        goal=f"{fan} fanidan {sinf}-sinf uchun "
             f"5 ta mukammal test savol yozish",
        backstory=f"""Sen O'zbekistondagi eng yaxshi 
                    test savollari yozuvchisisаn.
                    Sening savollaringni o'quvchilar
                    sevadi — qiyin emas, oson ham emas!
                    Har savol o'rgatuvchi va qiziqarli.
                    FAQAT O'zbek tilida yozasan!""",
        verbose=True,
        allow_delegation=False,
        llm_config={
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": GROQ_API_KEY,
        }
    )

    # AGENT 3 — Sifat Nazoratchi
    nazoratchi = Agent(
        role="Ta'lim sifat nazoratchi",
        goal="Savollarni tekshirish va tasdiqlash",
        backstory="""Sen O'zbek ta'lim standartlarini
                    yaxshi biluvchi ekspertsan.
                    Grammatika xatolarini topasan.
                    Faktlarning to'g'riligini tekshirasan.
                    Faqat sifatli savollarni tasdiqlaysan!""",
        verbose=True,
        allow_delegation=False,
        llm_config={
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": GROQ_API_KEY,
        }
    )

    return tadqiqotchi, savol_yozuvchi, nazoratchi


# ══════════════════════════════════════════
# 📋 VAZIFALAR
# ══════════════════════════════════════════

def vazifalar_yaratish(fan, sinf, mavzu, tadqiqotchi, savol_yozuvchi, nazoratchi):

    # VAZIFA 1 — Tadqiqot
    tadqiqot = Task(
        description=f"""
        Fan: {fan}
        Sinf: {sinf}
        Mavzu: {mavzu}
        
        Shu mavzu haqida:
        1. 5 ta qiziqarli fakt top
        2. O'quvchilar bilishi kerak bo'lgan
           asosiy tushunchalar
        3. Kundalik hayotdagi misolllar
        
        Natijani O'zbek tilida yoz!
        """,
        agent=tadqiqotchi,
        expected_output="5 ta fakt va asosiy tushunchalar ro'yxati"
    )

    # VAZIFA 2 — Savol yozish
    savol_yozish = Task(
        description=f"""
        Tadqiqotchi topgan faktlar asosida
        {fan} fanidan {sinf}-sinf uchun
        AYNAN 5 ta test savol yoz!
        
        MUHIM QOIDALAR:
        - O'zbek tilida yoz!
        - Har savol — aniq va tushunarli
        - 4 ta variant (A, B, C, D)
        - Faqat 1 ta to'g'ri javob
        - Izoh — nima uchun to'g'ri ekanini tushuntir
        
        FAQAT JSON formatda yoz, boshqa hech narsa yozma:
        [
          {{
            "s": "Savol matni bu yerga",
            "v": ["A variant", "B variant", "C variant", "D variant"],
            "t": 0,
            "i": "Izoh: nima uchun A to'g'ri"
          }}
        ]
        
        t = to'g'ri javob indeksi (0=A, 1=B, 2=C, 3=D)
        """,
        agent=savol_yozuvchi,
        expected_output="5 ta JSON formatdagi savol"
    )

    # VAZIFA 3 — Tekshirish
    tekshirish = Task(
        description=f"""
        Yozilgan savollarni tekshir:
        
        ✅ O'zbek tili to'g'rimi?
        ✅ Faktlar aniqmi?
        ✅ To'g'ri javob rostdan to'g'rimi?
        ✅ {sinf}-sinf darajasiga mosmi?
        ✅ JSON format to'g'rimi?
        
        Agar xato bo'lsa — tuzat!
        
        FAQAT to'g'rilangan JSON qaytар:
        [
          {{
            "s": "savol",
            "v": ["A", "B", "C", "D"],
            "t": 0,
            "i": "izoh"
          }}
        ]
        """,
        agent=nazoratchi,
        expected_output="Tekshirilgan va to'g'rilangan 5 ta savol JSON"
    )

    return tadqiqot, savol_yozish, tekshirish


# ══════════════════════════════════════════
# 💾 DATABASE GA SAQLASH
# ══════════════════════════════════════════

def savollarni_saqlash(fan: str, sinf: str, yangi_savollar: list) -> bool:
    try:
        # Mavjud database ni o'qi
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {"users": {}, "stats": {}}

        # Yangi bo'lim yaratish — agent savollar
        if "agent_savollar" not in db:
            db["agent_savollar"] = {}

        if fan not in db["agent_savollar"]:
            db["agent_savollar"][fan] = {}

        if sinf not in db["agent_savollar"][fan]:
            db["agent_savollar"][fan][sinf] = []

        # Yangi savollarni qo'sh
        db["agent_savollar"][fan][sinf].extend(yangi_savollar)

        # Oxirgi 50 ta saqlash (eski larni o'chir)
        if len(db["agent_savollar"][fan][sinf]) > 50:
            db["agent_savollar"][fan][sinf] = \
                db["agent_savollar"][fan][sinf][-50:]

        # Saqlash
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        print(f"✅ {fan} ({sinf}-sinf): {len(yangi_savollar)} ta savol saqlandi!")
        return True

    except Exception as e:
        print(f"❌ Saqlash xatosi: {e}")
        return False


# ══════════════════════════════════════════
# 📨 TELEGRAM XABAR
# ══════════════════════════════════════════

async def adminga_xabar(matn: str):
    if not BOT_TOKEN or not ADMIN_ID:
        print("⚠️ Bot token yoki Admin ID yo'q!")
        return

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            await session.post(url, json={
                "chat_id": ADMIN_ID,
                "text": matn,
                "parse_mode": "Markdown"
            })
        print("📨 Adminga xabar yuborildi!")
    except Exception as e:
        print(f"❌ Telegram xatosi: {e}")


# ══════════════════════════════════════════
# 🚀 ASOSIY FUNKSIYA
# ══════════════════════════════════════════

def agent_ishga_tushur(fan: str = None, sinf: str = "7"):

    # Fan tanlanmagan bo'lsa — bugungi fan
    if not fan:
        fan = bugungi_fan()

    mavzu = bugungi_mavzu(fan)

    print(f"""
╔══════════════════════════════════╗
║   🤖 ZakovatBot Agent Ishga Tushdi!
║   📚 Fan: {fan}
║   🎓 Sinf: {sinf}
║   📖 Mavzu: {mavzu}
║   ⏰ Vaqt: {datetime.now().strftime('%H:%M:%S')}
╚══════════════════════════════════╝
    """)

    try:
        # Agentlarni yaratish
        tadqiqotchi, savol_yozuvchi, nazoratchi = \
            agentlar_yaratish(fan, sinf, mavzu)

        # Vazifalarni yaratish
        tadqiqot, savol_yozish, tekshirish = vazifalar_yaratish(
            fan, sinf, mavzu,
            tadqiqotchi, savol_yozuvchi, nazoratchi
        )

        # Jamoa tuzish
        jamoa = Crew(
            agents=[tadqiqotchi, savol_yozuvchi, nazoratchi],
            tasks=[tadqiqot, savol_yozish, tekshirish],
            process=Process.sequential,
            verbose=True
        )

        # ISHGA TUS!
        print("\n🔄 Agent ishlayapti...\n")
        natija = jamoa.kickoff()
        natija_matn = str(natija)

        # JSON ajratib olish
        start = natija_matn.find("[")
        end   = natija_matn.rfind("]") + 1

        if start != -1 and end > start:
            savollar = json.loads(natija_matn[start:end])

            # Database ga saqlash
            saqlandi = savollarni_saqlash(fan, sinf, savollar)

            if saqlandi:
                # Adminga xabar
                xabar = f"""
🤖 *ZakovatBot Agent — Yangi Savollar!*

📚 Fan: *{fan}*
🎓 Sinf: *{sinf}-sinf*
📖 Mavzu: *{mavzu}*
✅ Savollar: *{len(savollar)} ta*
⏰ Vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Yangi savollar database ga saqlandi!
O'quvchilar endi bu savollardan foydalana oladi! 🎉
                """
                asyncio.run(adminga_xabar(xabar))

                print(f"""
╔══════════════════════════════════╗
║   ✅ MUVAFFAQIYATLI TUGADI!
║   📊 {len(savollar)} ta yangi savol saqlandi!
╚══════════════════════════════════╝
                """)
                return savollar
        else:
            print("❌ JSON topilmadi!")
            return []

    except Exception as e:
        print(f"❌ Agent xatosi: {e}")
        xabar = f"⚠️ Agent xatosi: {e}"
        asyncio.run(adminga_xabar(xabar))
        return []


# ══════════════════════════════════════════
# ⏰ AVTOMATIK JADVAL
# ══════════════════════════════════════════

def jadval_ishga_tushur():
    print("""
╔══════════════════════════════════════╗
║   ⏰ ZakovatBot Jadval Ishga Tushdi!
║                                      
║   📅 Har kuni:                       
║   🕘 09:00 — Matematika              
║   🕐 13:00 — Tarix                   
║   🕘 19:00 — Biologiya               
║   🕙 21:00 — Bugungi fan (auto)      
╚══════════════════════════════════════╝
    """)

    # Har kuni aniq vaqtlarda
    schedule.every().day.at("09:00").do(
        agent_ishga_tushur, fan="Matematika", sinf="7"
    )
    schedule.every().day.at("13:00").do(
        agent_ishga_tushur, fan="Tarix", sinf="8"
    )
    schedule.every().day.at("19:00").do(
        agent_ishga_tushur, fan="Biologiya", sinf="9"
    )
    schedule.every().day.at("21:00").do(
        agent_ishga_tushur  # Bugungi fan avtomatik
    )

    print("✅ Jadval sozlandi! Agent kutmoqda...\n")

    # Doim ishlaydi
    while True:
        schedule.run_pending()
        time.sleep(60)  # Har daqiqa tekshiradi


# ══════════════════════════════════════════
# ▶️ ISHGA TUSHIRISH
# ══════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Bitta test — hozir ishga tushur
            print("🧪 TEST REJIMI — bitta savol to'plami yaratilmoqda...")
            agent_ishga_tushur(fan="Tarix", sinf="7")

        elif sys.argv[1] == "jadval":
            # Avtomatik jadval
            jadval_ishga_tushur()

        elif sys.argv[1] == "fan" and len(sys.argv) > 2:
            # Aniq fan uchun
            fan = sys.argv[2]
            sinf = sys.argv[3] if len(sys.argv) > 3 else "7"
            agent_ishga_tushur(fan=fan, sinf=sinf)
    else:
        # Standart — test rejimi
        print("📌 Foydalanish:")
        print("  python zakovatbot_agent.py test          — bitta test")
        print("  python zakovatbot_agent.py jadval        — avtomatik jadval")
        print("  python zakovatbot_agent.py fan Tarix 8  — aniq fan/sinf")
        print()
        print("🚀 Test rejimi boshlanmoqda...")
        agent_ishga_tushur(fan="Tarix", sinf="7")
