"""
╔══════════════════════════════════════════════════════╗
║         ZAKOVATBOT — TO'LIQ VERSIYA 2.0             ║
║      O'zbek ta'lim platformasi (1-11 sinf)          ║
║                                                      ║
║  ✅ 1-11 sinf, 14 fan                               ║
║  ✅ CHEKSIZ savollar (Groq AI)                      ║
║  ✅ Takrorlanmas savollar (kesh tizimi)              ║
║  ✅ Professional profil                              ║
║  ✅ Streak + Gamifikatsiya                           ║
║  ✅ Referral tizimi                                  ║
║  ✅ O'qituvchi PDF generator                        ║
║  ✅ Premium tizimi                                   ║
╚══════════════════════════════════════════════════════╝

O'RNATISH:
pip install python-telegram-bot reportlab aiohttp

ISHGA TUSHIRISH:
python zakovatbot_full_v2.py
"""

import logging, json, os, random, asyncio, aiohttp
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ══════════════════════════════════════════
# ⚙️ SOZLAMALAR — BU YERNI TO'LDIRING!
# ══════════════════════════════════════════
BOT_TOKEN    = "8260900161:AAGModPJoxZQIlTL5_B5u4NagbFUUSY_MSo"
GROQ_API_KEY = "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"   # groq.com dan oling (BEPUL!)
ADMIN_ID     = 1967786876                          # @userinfobot ga yozing — sizning ID

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO,
    handlers=[logging.FileHandler("zakovatbot.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════
# 📚 FANLAR TIZIMI
# ══════════════════════════════════════════
SINF_FANLAR = {
    "1": ["Matematika", "O'qish", "Dunyo"],
    "2": ["Matematika", "O'zbek tili", "Dunyo", "Ingliz tili"],
    "3": ["Matematika", "O'zbek tili", "Dunyo", "Ingliz tili"],
    "4": ["Matematika", "O'zbek tili", "Tabiatshunoslik", "Ingliz tili", "Tarix"],
    "5": ["Matematika", "O'zbek tili", "Tarix", "Ingliz tili", "Biologiya", "Geografiya"],
    "6": ["Matematika", "O'zbek tili", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika"],
    "7": ["Algebra", "Geometriya", "O'zbek tili", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo"],
    "8": ["Algebra", "Geometriya", "O'zbek tili va adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo"],
    "9": ["Algebra", "Geometriya", "O'zbek tili va adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo", "Informatika"],
    "10": ["Matematika", "O'zbek tili va adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo", "Informatika"],
    "11": ["Matematika", "O'zbek tili va adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo", "Informatika", "Nemis tili"],
}

FAN_EMOJI = {
    "Matematika": "🔢", "Algebra": "📐", "Geometriya": "📏",
    "O'zbek tili": "📝", "O'zbek tili va adabiyot": "📝", "O'qish": "📖",
    "Tarix": "📜", "Ingliz tili": "🇬🇧", "Nemis tili": "🇩🇪",
    "Biologiya": "🌿", "Geografiya": "🌍", "Fizika": "⚡",
    "Kimyo": "🧪", "Informatika": "💻", "Dunyo": "🌐", "Tabiatshunoslik": "🌱",
}

# ══════════════════════════════════════════
# 📝 ZAXIRA SAVOLLAR (Groq ishlamasa)
# ══════════════════════════════════════════
ZAXIRA = {
    "Matematika": [
        {"s": "2 + 2 = ?", "v": ["3","4","5","6"], "t": 1, "i": "2+2=4!"},
        {"s": "10 x 5 = ?", "v": ["40","45","50","55"], "t": 2, "i": "10x5=50!"},
        {"s": "100 / 4 = ?", "v": ["20","25","30","35"], "t": 1, "i": "100/4=25!"},
        {"s": "3 daraja 2 = ?", "v": ["6","8","9","12"], "t": 2, "i": "3 daraja 2 = 9!"},
        {"s": "16 ning ildizi = ?", "v": ["2","3","4","5"], "t": 2, "i": "16 ildizi = 4!"},
        {"s": "7 x 8 = ?", "v": ["54","56","58","60"], "t": 1, "i": "7x8=56!"},
        {"s": "1000 - 357 = ?", "v": ["633","643","653","663"], "t": 1, "i": "1000-357=643!"},
    ],
    "Tarix": [
        {"s": "Amir Temur qachon tug'ilgan?", "v": ["1326","1336","1346","1356"], "t": 1, "i": "1336-yil!"},
        {"s": "O'zbekiston mustaqilligi?", "v": ["1990","1991","1992","1993"], "t": 1, "i": "1991-yil 1-sentabr!"},
        {"s": "Al-Xorazmiy qaysi sohada mashhur?", "v": ["Tarix","Matematika","Adabiyot","Musiqa"], "t": 1, "i": "Algebra asoschisi!"},
        {"s": "Ibn Sino asosiy kasbi?", "v": ["Tarixchi","Shoir","Tabib","Matematik"], "t": 2, "i": "Buyuk tabib va olim!"},
        {"s": "Ipak yo'li qayerdan o'tgan?", "v": ["Afrika","Yevropa","O'rta Osiyo","Amerika"], "t": 2, "i": "O'rta Osiyo orqali!"},
        {"s": "Ulug'bek kim edi?", "v": ["Shoir","Astronom","Jangchi","Savdogar"], "t": 1, "i": "Ulug'bek buyuk astronom!"},
    ],
    "Biologiya": [
        {"s": "Fotosintez qayerda sodir bo'ladi?", "v": ["Ildiz","Barg","Gul","Meva"], "t": 1, "i": "Bargdagi xloroplastlarda!"},
        {"s": "Odamda nechta suyak bor?", "v": ["186","196","206","216"], "t": 2, "i": "206 ta suyak!"},
        {"s": "DNA nima?", "v": ["Oqsil","Yog'","Genetik ma'lumot","Vitamin"], "t": 2, "i": "Genetik ma'lumot tashuvchi!"},
        {"s": "O'simliklar nima yutadi?", "v": ["O2","CO2","N2","H2"], "t": 1, "i": "CO2 yutib O2 chiqaradi!"},
        {"s": "Eng katta organ?", "v": ["Yurak","Jigar","Teri","O'pka"], "t": 2, "i": "Teri eng katta organ!"},
    ],
    "Fizika": [
        {"s": "Yorug'lik tezligi (km/s)?", "v": ["100000","200000","300000","400000"], "t": 2, "i": "300,000 km/s!"},
        {"s": "Suv qaynash harorati?", "v": ["50","80","100","120"], "t": 2, "i": "100 daraja C!"},
        {"s": "Kuch birligi?", "v": ["Joul","Vatt","Nyuton","Paskal"], "t": 2, "i": "Kuch = Nyuton!"},
        {"s": "Tezlik formulasi?", "v": ["v=a/t","v=s/t","v=s*t","v=F/m"], "t": 1, "i": "v = s/t!"},
    ],
    "Kimyo": [
        {"s": "Suv formulasi?", "v": ["CO2","H2O","NaCl","O2"], "t": 1, "i": "H2O!"},
        {"s": "Mis elementi belgisi?", "v": ["Co","Cu","Cr","Ca"], "t": 1, "i": "Cu = Cuprum!"},
        {"s": "Eng yengil element?", "v": ["Geliy","Vodorod","Litiy","Uglerod"], "t": 1, "i": "Vodorod (H)!"},
        {"s": "NaCl nima?", "v": ["Shakar","Osh tuzi","Soda","Sirka"], "t": 1, "i": "Natriy xlorid = Osh tuzi!"},
    ],
    "Ingliz tili": [
        {"s": "Hello so'zining ma'nosi?", "v": ["Xayr","Salom","Rahmat","Kechirasiz"], "t": 1, "i": "Hello = Salom!"},
        {"s": "Book so'zining ma'nosi?", "v": ["Qalam","Daftar","Kitob","Stol"], "t": 2, "i": "Book = Kitob!"},
        {"s": "How old are you? — tarjima?", "v": ["Qayerdasan?","Nechchi yoshsan?","Noming nima?","Yaxshimisan?"], "t": 1, "i": "Nechchi yoshsan?"},
        {"s": "I am a student — tarjima?", "v": ["Men o'qituvchiman","Men o'quvchiman","Men shifokorman","Men sportchiman"], "t": 1, "i": "I am a student = Men o'quvchiman!"},
    ],
    "Geografiya": [
        {"s": "O'zbekiston poytaxti?", "v": ["Samarqand","Buxoro","Toshkent","Namangan"], "t": 2, "i": "Toshkent — poytaxt!"},
        {"s": "Dunyo eng katta okeani?", "v": ["Atlantika","Hind","Tinch","Arktika"], "t": 2, "i": "Tinch okeani eng katta!"},
        {"s": "Amudaryo qayerga quyiladi?", "v": ["Kaspiy","Orol","Balxash","Qoradeniz"], "t": 1, "i": "Orol dengiziga!"},
        {"s": "O'zbekistonda nechta viloyat?", "v": ["10","12","14","16"], "t": 2, "i": "14 ta viloyat!"},
    ],
}

# ══════════════════════════════════════════
# 💾 DATABASE
# ══════════════════════════════════════════
DB_FILE = "zakovatbot_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "kesh": {}, "stats": {"total_users": 0, "total_answers": 0, "start_date": str(date.today())}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(user_id, first_name="", username=""):
    db = load_db(); uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "id": user_id, "ism": first_name, "username": username,
            "sinf": None, "ball": 0, "togri": 0, "notogri": 0,
            "streak": 0, "max_streak": 0, "bugungi_savol": 0,
            "oxirgi_kun": str(date.today()), "premium": False,
            "premium_tugash": None, "referral_kod": f"REF{user_id}",
            "referral_count": 0, "yutuqlar": [], "korilgan": [],
            "qoshilgan": str(datetime.now())[:16], "oxirgi_faollik": str(datetime.now())[:16],
        }
        db["stats"]["total_users"] += 1; save_db(db)
    else:
        if db["users"][uid]["oxirgi_kun"] != str(date.today()):
            db["users"][uid]["bugungi_savol"] = 0
            db["users"][uid]["oxirgi_kun"] = str(date.today())
            save_db(db)
    return db["users"][uid]

def update_user(user_id, data):
    db = load_db(); uid = str(user_id)
    if uid in db["users"]:
        db["users"][uid].update(data)
        db["users"][uid]["oxirgi_faollik"] = str(datetime.now())[:16]
        save_db(db)

def javob_berdi(user_id, togri):
    db = load_db(); uid = str(user_id)
    if uid not in db["users"]: return get_user(user_id)
    u = db["users"][uid]
    if togri:
        u["togri"] += 1; u["ball"] += 10; u["streak"] += 1; u["bugungi_savol"] += 1
        if u["streak"] > u["max_streak"]: u["max_streak"] = u["streak"]
    else:
        u["notogri"] += 1; u["streak"] = 0; u["bugungi_savol"] += 1
    db["stats"]["total_answers"] = db["stats"].get("total_answers", 0) + 1
    save_db(db); return u

def get_reyting(limit=10):
    db = load_db()
    return sorted(db["users"].values(), key=lambda x: x["ball"], reverse=True)[:limit]

def get_referral_user(kod):
    db = load_db()
    for u in db["users"].values():
        if u.get("referral_kod") == kod: return u
    return None

def savol_korildi(user_id, savol_matni):
    db = load_db(); uid = str(user_id)
    if uid in db["users"]:
        k = db["users"][uid].get("korilgan", [])
        if savol_matni not in k:
            k.append(savol_matni)
            db["users"][uid]["korilgan"] = k[-100:]
            save_db(db)

# ══════════════════════════════════════════
# 🎮 GAMIFIKATSIYA
# ══════════════════════════════════════════
DARAJALAR = [
    (0,50,"Yangi o'quvchi"), (50,200,"O'quvchi"), (200,500,"Bilimdon"),
    (500,1000,"Usta"), (1000,2000,"Champion"), (2000,5000,"Zakovat ustasi"), (5000,9999,"AKADEMIK"),
]
YUTUQLAR = {
    "birinchi_javob": {"nom": "Birinchi qadam",  "tavsif": "Birinchi savolga javob bering"},
    "streak_5":       {"nom": "5 streak",         "tavsif": "5 ta ketma-ket to'g'ri javob"},
    "streak_10":      {"nom": "10 streak",         "tavsif": "10 ta ketma-ket to'g'ri javob"},
    "ball_100":       {"nom": "100 ball",          "tavsif": "100 ball yig'ing"},
    "ball_500":       {"nom": "500 ball",          "tavsif": "500 ball yig'ing"},
    "ball_1000":      {"nom": "1000 ball",         "tavsif": "1000 ball yig'ing"},
    "referral_1":     {"nom": "Do'st taklif",      "tavsif": "1 ta do'stni taklif qiling"},
    "referral_5":     {"nom": "Jamoa",             "tavsif": "5 ta do'stni taklif qiling"},
}

def get_daraja(ball):
    for mn, mx, nom in DARAJALAR:
        if mn <= ball < mx: return nom
    return "AKADEMIK"

def check_yutuqlar(user):
    mavjud = user.get("yutuqlar", [])
    checks = {
        "birinchi_javob": user["togri"] >= 1, "streak_5": user["max_streak"] >= 5,
        "streak_10": user["max_streak"] >= 10, "ball_100": user["ball"] >= 100,
        "ball_500": user["ball"] >= 500, "ball_1000": user["ball"] >= 1000,
        "referral_1": user["referral_count"] >= 1, "referral_5": user["referral_count"] >= 5,
    }
    return [k for k, v in checks.items() if v and k not in mavjud]

# ══════════════════════════════════════════
# 🎨 KLAVIATURA
# ══════════════════════════════════════════
def main_menu(premium=False):
    kb = [
        [KeyboardButton("📚 O'rganish"), KeyboardButton("🏆 Reyting")],
        [KeyboardButton("👤 Profilim"),  KeyboardButton("🎯 Tezkor test")],
        [KeyboardButton("👥 Do'stlar"),  KeyboardButton("ℹ️ Yordam")],
    ]
    if premium: kb.append([KeyboardButton("📄 PDF Test"), KeyboardButton("⚙️ Sozlamalar")])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def sinf_menu():
    kb, row = [], []
    for s in range(1, 12):
        row.append(InlineKeyboardButton(f"{s}-sinf", callback_data=f"sinf_{s}"))
        if len(row) == 3: kb.append(row); row = []
    if row: kb.append(row)
    return InlineKeyboardMarkup(kb)

def fanlar_menu(sinf):
    fanlar = SINF_FANLAR.get(str(sinf), []); kb, row = [], []
    for fan in fanlar:
        row.append(InlineKeyboardButton(f"{FAN_EMOJI.get(fan,'📚')} {fan}", callback_data=f"fan_{sinf}_{fan}"))
        if len(row) == 2: kb.append(row); row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_sinf")])
    return InlineKeyboardMarkup(kb)

def savol_kb(fan, sinf, savol, idx):
    hrf = ["A","B","C","D"]
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{hrf[i]}) {v}", callback_data=f"j_{fan}_{sinf}_{idx}_{i}")] for i,v in enumerate(savol["v"])])

# ══════════════════════════════════════════
# 🤖 GROQ AI — CHEKSIZ SAVOLLAR
# ══════════════════════════════════════════
async def groq_savol_tuz(fan, sinf, soni=15):
    if not GROQ_API_KEY or GROQ_API_KEY == "BU_YERGA_GROQ_API_KEY": return []
    prompt = f"""Sen O'zbek maktabi uchun professional savol tuzuvchisan.
Fan: {fan}, Sinf: {sinf}-sinf
{soni} ta test savol tuz. {sinf}-sinf darajasiga mos bo'lsin. O'zbek tilida yoz!
FAQAT JSON formatda javob ber, boshqa narsa yozma:
[{{"s":"Savol matni","v":["A","B","C","D"],"t":0,"i":"Nima uchun to'g'ri - izoh"}}]
t = to'g'ri javob indeksi (0=A, 1=B, 2=C, 3=D)"""
    try:
        async with aiohttp.ClientSession() as ses:
            async with ses.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens":3000, "temperature":0.8},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as r:
                d = await r.json()
                c = d["choices"][0]["message"]["content"]
                st, en = c.find("["), c.rfind("]")+1
                if st != -1 and en > st: return json.loads(c[st:en])
    except Exception as e:
        logger.error(f"Groq xatosi: {e}")
    return []

async def get_savol(fan, sinf, user_id):
    """ASOSIY FUNKSIYA: Har doim yangi, takrorlanmas savol!"""
    db = load_db(); k = f"{fan}_{sinf}"
    if "kesh" not in db: db["kesh"] = {}
    kesh = db["kesh"].get(k, [])

    # Keshda 5 dan kam — Groq dan yangilash
    if len(kesh) < 5:
        logger.info(f"Groq: {fan} {sinf}-sinf uchun savollar yuklanmoqda...")
        yangi = await groq_savol_tuz(fan, sinf, 15)
        if yangi:
            kesh = kesh + yangi
            db["kesh"][k] = kesh[-60:]  # Max 60 ta saqlash
            save_db(db)
            logger.info(f"OK: {len(yangi)} ta yangi savol saqlandi!")

    # Groq ishlamasa — zaxira
    if not kesh:
        fn = fan.replace(" va adabiyot","").replace("Algebra","Matematika").replace("Geometriya","Matematika")
        kesh = ZAXIRA.get(fn, ZAXIRA.get("Matematika", []))

    # Foydalanuvchi ko'rmagan savolni tanlash
    uid = str(user_id)
    korilgan = db.get("users",{}).get(uid,{}).get("korilgan",[])
    yangi_s = [s for s in kesh if s["s"] not in korilgan]

    # Hammasi ko'rilgan bo'lsa — reset
    if not yangi_s:
        update_user(user_id, {"korilgan": []})
        yangi_s = kesh

    savol = random.choice(yangi_s)
    idx = kesh.index(savol) if savol in kesh else 0
    return savol, idx

# ══════════════════════════════════════════
# 📄 PDF GENERATOR
# ══════════════════════════════════════════
def pdf_test_yaratish(fan, sinf, mavzu, oquvtchi, sana, savol_soni=20):
    fn = fan.replace(" va adabiyot","").replace("Algebra","Matematika").replace("Geometriya","Matematika")
    savollar = list(ZAXIRA.get(fn, ZAXIRA.get("Matematika",[])))
    while len(savollar) < savol_soni: savollar = savollar + savollar
    savollar = random.sample(savollar, min(savol_soni, len(savollar)))
    test_s = savollar[:int(savol_soni*0.7)]; ochiq_s = savollar[int(savol_soni*0.7):]
    test_son = len(test_s); ochiq_son = len(ochiq_s)

    fname = f"/tmp/test_{fan}_{sinf}_{datetime.now().strftime('%H%M%S')}.pdf"
    KOK=colors.HexColor('#1a3a6b'); OCH=colors.HexColor('#e8f0fe')
    YASHIL=colors.HexColor('#27ae60'); KULRANG=colors.HexColor('#7f8c8d'); OCHIQ=colors.HexColor('#f5f5f5')

    doc=SimpleDocTemplate(fname,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    st=getSampleStyleSheet()
    ts=ParagraphStyle('T',parent=st['Normal'],fontSize=18,textColor=KOK,alignment=TA_CENTER,spaceAfter=6,fontName='Helvetica-Bold')
    ss=ParagraphStyle('S',parent=st['Normal'],fontSize=11,textColor=KULRANG,alignment=TA_CENTER,spaceAfter=4)
    hs=ParagraphStyle('H',parent=st['Normal'],fontSize=12,textColor=colors.white,spaceBefore=10,spaceAfter=6,fontName='Helvetica-Bold',leftIndent=6)
    qs=ParagraphStyle('Q',parent=st['Normal'],fontSize=11,textColor=KOK,spaceBefore=8,spaceAfter=4,fontName='Helvetica-Bold')
    os_=ParagraphStyle('O',parent=st['Normal'],fontSize=10.5,leftIndent=20,spaceAfter=2)
    is_=ParagraphStyle('I',parent=st['Normal'],fontSize=10)

    story=[]
    story+=[Paragraph("ZakovatBot — Ta'lim platformasi",ss),Paragraph(f"{fan.upper()} — {sinf}-SINF",ts),
            Paragraph(f"Mavzu: {mavzu}",ss),Spacer(1,0.3*cm),HRFlowable(width="100%",thickness=2,color=KOK),Spacer(1,0.3*cm)]

    inf=Table([[Paragraph(f"<b>Sinf:</b> {sinf}",is_),Paragraph(f"<b>Fan:</b> {fan}",is_),Paragraph(f"<b>Sana:</b> {sana}",is_)],
               [Paragraph(f"<b>Oqituvchi:</b> {oquvtchi}",is_),Paragraph(f"<b>Savol:</b> {savol_soni} ta",is_),Paragraph("<b>Ism:</b> ___________",is_)]],colWidths=[5.5*cm]*3)
    inf.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),OCHIQ),('GRID',(0,0),(-1,-1),0.5,colors.lightgrey),('PADDING',(0,0),(-1,-1),8)]))
    story+=[inf,Spacer(1,0.4*cm)]

    h1=Table([[Paragraph(f"  I QISM — TEST ({test_son} ta x 7 ball = {test_son*7} ball)",hs)]],colWidths=[16.5*cm])
    h1.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),KOK),('PADDING',(0,0),(-1,-1),8)]))
    story+=[h1,Spacer(1,0.3*cm)]

    def qblock(ql, start):
        b=[]; hrf=["A","B","C","D"]
        for i,q in enumerate(ql,start):
            b.append(Paragraph(f"<b>{i}.</b> {q['s']}",qs))
            for j,v in enumerate(q["v"]): b.append(Paragraph(f"{hrf[j]}) {v}",os_))
            b.append(Spacer(1,0.15*cm))
        return b

    ym=len(test_s)//2
    tbl=Table([[qblock(test_s[:ym],1),qblock(test_s[ym:],ym+1)]],colWidths=[8*cm,8*cm])
    tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEAFTER',(0,0),(0,-1),0.5,colors.lightgrey),('LEFTPADDING',(1,0),(1,-1),12),('RIGHTPADDING',(0,0),(0,-1),12)]))
    story+=[tbl,Spacer(1,0.4*cm),Paragraph("<b>Javoblar jadvali:</b>",is_),Spacer(1,0.1*cm)]

    hd=[Paragraph(f"<b>{i}</b>",ParagraphStyle('c',parent=st['Normal'],alignment=TA_CENTER,fontSize=10,fontName='Helvetica-Bold')) for i in range(1,test_son+1)]
    an=[Paragraph("____",ParagraphStyle('a',parent=st['Normal'],alignment=TA_CENTER,fontSize=12)) for _ in range(test_son)]
    for cs in range(0,test_son,10):
        ce=min(cs+10,test_son); n=ce-cs; w=16.5/n
        jt=Table([hd[cs:ce],an[cs:ce]],colWidths=[w*cm]*n)
        jt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey),('BACKGROUND',(0,0),(-1,0),OCH),('ALIGN',(0,0),(-1,-1),'CENTER'),('PADDING',(0,0),(-1,-1),6)]))
        story+=[jt,Spacer(1,0.15*cm)]

    if ochiq_s:
        h2=Table([[Paragraph(f"  II QISM — OCHIQ SAVOLLAR ({ochiq_son} ta)",hs)]],colWidths=[16.5*cm])
        h2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),YASHIL),('PADDING',(0,0),(-1,-1),8)]))
        story+=[Spacer(1,0.3*cm),h2,Spacer(1,0.3*cm)]
        for i,q in enumerate(ochiq_s,1):
            story.append(Paragraph(f"<b>{i}.</b> {q['s']}",qs))
            for _ in range(4): story.append(HRFlowable(width="100%",thickness=0.5,color=colors.lightgrey,spaceAfter=14))
            story.append(Spacer(1,0.2*cm))

    story+=[HRFlowable(width="100%",thickness=1,color=KOK),Spacer(1,0.2*cm),
            Table([[Paragraph("<i>ZakovatBot tomonidan | @ZakovatEduBot</i>",ParagraphStyle('f',parent=st['Normal'],fontSize=8,textColor=KULRANG,fontName='Helvetica-Oblique')),
                    Paragraph(f"<i>{sana}</i>",ParagraphStyle('f2',parent=st['Normal'],fontSize=8,textColor=KULRANG,alignment=1,fontName='Helvetica-Oblique'))]],colWidths=[10*cm,6.5*cm])]

    story.append(PageBreak())
    story+=[Paragraph("JAVOBLAR — FAQAT O'QITUVCHI UCHUN",ts),Paragraph(f"{fan} | {sinf}-sinf | {mavzu}",ss),
            Spacer(1,0.3*cm),HRFlowable(width="100%",thickness=2,color=KOK),Spacer(1,0.4*cm)]
    hrf=["A","B","C","D"]
    ch=[Paragraph(f"<b>{i}</b>",ParagraphStyle('ch',parent=st['Normal'],alignment=TA_CENTER,fontSize=10,fontName='Helvetica-Bold')) for i in range(1,test_son+1)]
    ca=[Paragraph(f"<b><font color='#27ae60'>{hrf[q['t']]}</font></b>",ParagraphStyle('ca',parent=st['Normal'],alignment=TA_CENTER,fontSize=14,fontName='Helvetica-Bold')) for q in test_s]
    for cs in range(0,test_son,10):
        ce=min(cs+10,test_son); n=ce-cs; w=16.5/n
        ct=Table([ch[cs:ce],ca[cs:ce]],colWidths=[w*cm]*n)
        ct.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey),('BACKGROUND',(0,0),(-1,0),KOK),('TEXTCOLOR',(0,0),(-1,0),colors.white),('BACKGROUND',(0,1),(-1,1),colors.HexColor('#e8fce8')),('ALIGN',(0,0),(-1,-1),'CENTER'),('PADDING',(0,0),(-1,-1),8)]))
        story+=[ct,Spacer(1,0.2*cm)]

    doc.build(story)
    return fname

# ══════════════════════════════════════════
# 📨 BUYRUQLAR
# ══════════════════════════════════════════
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; u=get_user(user.id,user.first_name,user.username or "")
    if context.args:
        ref=context.args[0]
        if ref.startswith("REF") and ref != u["referral_kod"]:
            ru=get_referral_user(ref)
            if ru:
                update_user(ru["id"],{"referral_count":ru["referral_count"]+1,"ball":ru["ball"]+100})
                update_user(user.id,{"ball":u["ball"]+50})
                await update.message.reply_text("Taklif orqali keldingiz! +50 ball!")
    st=f"{u['sinf']}-sinf" if u["sinf"] else "tanlanmagan"
    await update.message.reply_text(
        f"*Xush kelibsiz, {user.first_name}!*\nMen — *ZakovatBot* — AI o'qituvchingiz!\n\nSinf: {st} | Ball: {u['ball']} | {get_daraja(u['ball'])}\n\n1-11 sinf - CHEKSIZ AI savollar - PDF test",
        parse_mode="Markdown", reply_markup=main_menu(u["premium"]))
    if not u["sinf"]:
        await update.message.reply_text("*Qaysi sinfda o'qaysiz?*", parse_mode="Markdown", reply_markup=sinf_menu())

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; u=get_user(user.id,user.first_name)
    jami=u["togri"]+u["notogri"]; foiz=round(u["togri"]/jami*100) if jami else 0
    await update.message.reply_text(
        f"*{user.first_name}*\n{get_daraja(u['ball'])} | {u['ball']} ball\n\nTo'g'ri: {u['togri']} | Notogri: {u['notogri']} | {foiz}%\nStreak: {u['streak']} (Max: {u['max_streak']})\nBugun: {u['bugungi_savol']} ta | Yutuq: {len(u.get('yutuqlar',[]))} ta",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Yutuqlar",callback_data="yutuqlar"),InlineKeyboardButton("Sinf ozgartir",callback_data="sinf_ozgartir")]]))

async def reyting_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users=get_reyting(10); text="*TOP-10 REYTING*\n\n"
    medals=["1","2","3"]
    for i,u in enumerate(users,1):
        m=medals[i-1] if i<=3 else f"{i}."
        text+=f"{m}. {u['ism']} — *{u['ball']}* ball\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def dostlar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; u=get_user(user.id)
    bot=await context.bot.get_me()
    await update.message.reply_text(
        f"*DO'STLARNI TAKLIF QILING!*\nTaklif: {u['referral_count']} kishi | Bonus: {u['referral_count']*100} ball\n\nHavolangiz:\nhttps://t.me/{bot.username}?start={u['referral_kod']}",
        parse_mode="Markdown")

async def yordam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*YORDAM*\n/start /profile /reyting\n\nSinfni tanlang, Fan tanlang, Javob bering, Ball yiging!\nHar safar YANGI AI savol!\nPDF test — Premium uchun\n\n@ZakovatSupport",
        parse_mode="Markdown")

# ══════════════════════════════════════════
# 📩 XABARLAR
# ══════════════════════════════════════════
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text; user=update.effective_user; u=get_user(user.id,user.first_name)

    if text == "📚 O'rganish":
        if not u.get("sinf"):
            await update.message.reply_text("*Avval sinfingizni tanlang!*", parse_mode="Markdown", reply_markup=sinf_menu())
        else:
            await update.message.reply_text(f"*{u['sinf']}-sinf fanlari:*", parse_mode="Markdown", reply_markup=fanlar_menu(u["sinf"]))

    elif text == "🎯 Tezkor test":
        sinf=u.get("sinf","7"); fan=random.choice(SINF_FANLAR.get(str(sinf),["Matematika"]))
        await update.message.reply_text("AI savol tayyorlamoqda...")
        savol,idx=await get_savol(fan,str(sinf),user.id)
        await update.message.reply_text(f"{FAN_EMOJI.get(fan,'📚')} *{fan}* | {sinf}-sinf\n\n*{savol['s']}*\n\nJavobni tanlang:",
            parse_mode="Markdown", reply_markup=savol_kb(fan,str(sinf),savol,idx))

    elif text == "🏆 Reyting": await reyting_cmd(update, context)
    elif text == "👤 Profilim": await profile_cmd(update, context)
    elif text == "👥 Do'stlar": await dostlar_cmd(update, context)
    elif text == "ℹ️ Yordam": await yordam_cmd(update, context)

    elif text == "📄 PDF Test":
        if not u["premium"] and user.id != ADMIN_ID:
            await update.message.reply_text("Bu funksiya PREMIUM foydalanuvchilar uchun!")
        else:
            context.user_data["pdf_bosqich"]="sinf"
            await update.message.reply_text("*PDF Test — Sinf tanlang:*", parse_mode="Markdown", reply_markup=sinf_menu())

    elif text == "⚙️ Sozlamalar":
        db=load_db()
        await update.message.reply_text(
            f"*SOZLAMALAR*\nID: {user.id} | Sinf: {u['sinf'] or '?'} | Premium: {'Ha' if u['premium'] else 'Yoq'}\nJami: {db['stats']['total_users']} foydalanuvchi",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sinf ozgartir",callback_data="sinf_ozgartir")],[InlineKeyboardButton("Premium olish",callback_data="premium_info")]]))

    elif context.user_data.get("pdf_bosqich")=="mavzu":
        context.user_data["pdf_mavzu"]=text; context.user_data["pdf_bosqich"]="soni"
        await update.message.reply_text(f"Mavzu: *{text}*\n\nNechta savol?", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("10 ta",callback_data="pdf_soni_10"),InlineKeyboardButton("20 ta",callback_data="pdf_soni_20"),InlineKeyboardButton("30 ta",callback_data="pdf_soni_30")]]))
    else:
        await update.message.reply_text("Tugmalardan foydalaning!", reply_markup=main_menu(u["premium"]))

# ══════════════════════════════════════════
# 🔘 CALLBACK HANDLER
# ══════════════════════════════════════════
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    data=q.data; user=update.effective_user; u=get_user(user.id,user.first_name)

    # SINF
    if data.startswith("sinf_") and not data.startswith("sinf_ozgartir"):
        sinf=data.replace("sinf_","")
        if sinf.isdigit():
            update_user(user.id,{"sinf":sinf})
            await q.edit_message_text(f"*{sinf}-sinf tanlandi!*\n\nQaysi fan?", parse_mode="Markdown", reply_markup=fanlar_menu(sinf))

    elif data in ("sinf_ozgartir","back_sinf"):
        await q.edit_message_text("*Sinfingizni tanlang:*", parse_mode="Markdown", reply_markup=sinf_menu())

    # FAN
    elif data.startswith("fan_"):
        parts=data.split("_",2)
        if len(parts)==3:
            _,sinf,fan=parts
            await q.edit_message_text("AI savol tayyorlamoqda...")
            savol,idx=await get_savol(fan,sinf,user.id)
            await q.edit_message_text(f"{FAN_EMOJI.get(fan,'📚')} *{fan}* | {sinf}-sinf\n\n*{savol['s']}*\n\nJavobni tanlang:",
                parse_mode="Markdown", reply_markup=savol_kb(fan,sinf,savol,idx))

    # JAVOB
    elif data.startswith("j_"):
        parts=data.split("_"); fan=parts[1]; sinf=parts[2]; idx=int(parts[3]); tanlagan=int(parts[4])
        db=load_db(); k=f"{fan}_{sinf}"
        kesh=db.get("kesh",{}).get(k,[])
        if not kesh or idx>=len(kesh):
            fn=fan.replace(" va adabiyot","").replace("Algebra","Matematika").replace("Geometriya","Matematika")
            kesh=ZAXIRA.get(fn,ZAXIRA.get("Matematika",[]))
        savol=kesh[idx] if idx<len(kesh) else kesh[0]
        togri=savol["t"]; hrf=["A","B","C","D"]
        uu=javob_berdi(user.id,tanlagan==togri)
        savol_korildi(user.id,savol["s"])

        bonus=0
        if tanlagan==togri:
            if uu["streak"]==5: bonus=5; update_user(user.id,{"ball":uu["ball"]+5})
            elif uu["streak"]==10: bonus=10; update_user(user.id,{"ball":uu["ball"]+10})

        yy=check_yutuqlar(uu)
        if yy:
            db2=load_db(); db2["users"][str(user.id)]["yutuqlar"].extend(yy); save_db(db2)

        if tanlagan==togri:
            streak_t=f"\nStreak: {uu['streak']}" if uu["streak"]>1 else ""
            bonus_t=f"\nBonus: +{bonus} ball!" if bonus else ""
            res=f"TO'G'RI! +10 ball{streak_t}{bonus_t}\n\n{savol['i']}\n\nBall: *{uu['ball']}*"
        else:
            res=f"NOTOGRI!\nSiz: {hrf[tanlagan]}) {savol['v'][tanlagan]}\nTogri: {hrf[togri]}) *{savol['v'][togri]}*\n\n{savol['i']}"

        for y in yy: res+=f"\n\nYangi yutuq: {YUTUQLAR[y]['nom']}!"
        await q.edit_message_text(res, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Keyingi",callback_data=f"fan_{sinf}_{fan}"),InlineKeyboardButton("Fanlar",callback_data=f"sinf_{sinf}")]]))

    elif data=="yutuqlar":
        u=get_user(user.id); mavjud=u.get("yutuqlar",[])
        t="*YUTUQLARINGIZ*\n\n"
        for k,v in YUTUQLAR.items(): t+=f"{'OK' if k in mavjud else 'x'} {v['nom']} - {v['tavsif']}\n"
        await q.edit_message_text(t, parse_mode="Markdown")

    elif data=="premium_info":
        await q.edit_message_text("*PREMIUM*\nCheksiz savol + PDF generator + Statistika\n\n1 oy: 29,000 som | 3 oy: 75,000 som | 1 yil: 250,000 som\n@ZakovatSupport", parse_mode="Markdown")

    elif context.user_data.get("pdf_bosqich")=="sinf" and data.startswith("sinf_"):
        sinf=data.replace("sinf_","")
        if sinf.isdigit():
            context.user_data["pdf_sinf"]=sinf; context.user_data["pdf_bosqich"]="fan"
            await q.edit_message_text(f"Sinf: *{sinf}*\n\nQaysi fan?", parse_mode="Markdown", reply_markup=fanlar_menu(sinf))

    elif context.user_data.get("pdf_bosqich")=="fan" and data.startswith("fan_"):
        parts=data.split("_",2)
        if len(parts)==3:
            _,sinf,fan=parts; context.user_data["pdf_fan"]=fan; context.user_data["pdf_bosqich"]="mavzu"
            await q.edit_message_text(f"Fan: *{fan}*\n\nMavzuni yozing:", parse_mode="Markdown")

    elif data.startswith("pdf_soni_"):
        soni=int(data.replace("pdf_soni_","")); fan=context.user_data.get("pdf_fan","Tarix")
        sinf=context.user_data.get("pdf_sinf","7"); mavzu=context.user_data.get("pdf_mavzu","Umumiy")
        await q.edit_message_text("PDF tayyorlanmoqda...")
        try:
            pf=pdf_test_yaratish(fan,sinf,mavzu,u["ism"],str(date.today()),soni)
            with open(pf,"rb") as f:
                await context.bot.send_document(chat_id=user.id,document=f,filename=f"Test_{fan}_{sinf}sinf.pdf",
                    caption=f"*{fan} | {sinf}-sinf | {mavzu}*\n{soni} ta savol",parse_mode="Markdown")
            os.remove(pf); context.user_data.clear()
        except Exception as e:
            logger.error(f"PDF: {e}"); await context.bot.send_message(user.id,"PDF xatosi!")

# ══════════════════════════════════════════
# ISHGA TUSHIRISH
# ══════════════════════════════════════════
def main():
    print("ZAKOVATBOT v2.0 ISHGA TUSHDI!")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",   start_cmd))
    app.add_handler(CommandHandler("help",    yordam_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("reyting", reyting_cmd))
    app.add_handler(CommandHandler("dostlar", dostlar_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot ishlayapti! Ctrl+C - toxtatish")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
