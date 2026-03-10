"""
ZAKOVATBOT v3.0 - O'zbek ta'lim platformasi
✅ O'qituvchi panel | ✅ AI Repetitor | ✅ Premium | ✅ PDF Pro
"""
import logging, json, os, random, asyncio, aiohttp, re
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN    = "8260900161:AAGModPJoxZQIlTL5_B5u4NagbFUUSY_MSo"
GROQ_API_KEY = "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"
ADMIN_ID     =  1967786876  
BEPUL_LIMIT  = 10
TEACHER_LIMIT = 3

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO,
    handlers=[logging.FileHandler("zakovatbot.log", encoding="utf-8"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

SINF_FANLAR = {
    "1":["Matematika","O'qish","Dunyo"],
    "2":["Matematika","O'zbek tili","Dunyo","Ingliz tili"],
    "3":["Matematika","O'zbek tili","Dunyo","Ingliz tili"],
    "4":["Matematika","O'zbek tili","Tabiatshunoslik","Ingliz tili","Tarix"],
    "5":["Matematika","O'zbek tili","Tarix","Ingliz tili","Biologiya","Geografiya"],
    "6":["Matematika","O'zbek tili","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika"],
    "7":["Algebra","Geometriya","O'zbek tili","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika","Kimyo"],
    "8":["Algebra","Geometriya","O'zbek tili va adabiyot","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika","Kimyo"],
    "9":["Algebra","Geometriya","O'zbek tili va adabiyot","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika","Kimyo","Informatika"],
    "10":["Matematika","O'zbek tili va adabiyot","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika","Kimyo","Informatika"],
    "11":["Matematika","O'zbek tili va adabiyot","Tarix","Ingliz tili","Biologiya","Geografiya","Fizika","Kimyo","Informatika","Nemis tili"],
}
FAN_EMOJI = {
    "Matematika":"🔢","Algebra":"📐","Geometriya":"📏","O'zbek tili":"📝",
    "O'zbek tili va adabiyot":"📝","O'qish":"📖","Tarix":"📜","Ingliz tili":"🇬🇧",
    "Nemis tili":"🇩🇪","Biologiya":"🌿","Geografiya":"🌍","Fizika":"⚡",
    "Kimyo":"🧪","Informatika":"💻","Dunyo":"🌐","Tabiatshunoslik":"🌱",
}
QIYINLIK_NOMI = {"oson":"Oson 🟢","urta":"O'rta 🟡","qiyin":"Qiyin 🔴"}

ZAXIRA = {
    "Matematika":[
        {"s":"2³ = ?","v":["4","6","8","9"],"t":2,"i":"2³=2×2×2=8"},
        {"s":"√144 = ?","v":["10","11","12","13"],"t":2,"i":"√144=12"},
        {"s":"7×8 = ?","v":["54","56","58","60"],"t":1,"i":"7×8=56"},
        {"s":"15% dan 200 = ?","v":["20","25","30","35"],"t":2,"i":"200×0.15=30"},
        {"s":"1/2 + 1/3 = ?","v":["2/5","5/6","3/5","2/6"],"t":1,"i":"3/6+2/6=5/6"},
    ],
    "Tarix":[
        {"s":"Amir Temur qachon tug'ilgan?","v":["1326","1336","1346","1356"],"t":1,"i":"1336-yil, Kesh"},
        {"s":"O'zbekiston mustaqilligi?","v":["1990","1991","1992","1993"],"t":1,"i":"1991-yil 1-sentabr"},
        {"s":"Ulug'bek rasadxonasi qayerda?","v":["Buxoro","Toshkent","Samarqand","Xiva"],"t":2,"i":"Samarqandda, 1428"},
        {"s":"Ipak yo'li qayerdan o'tgan?","v":["Afrika","Yevropa","O'rta Osiyo","Amerika"],"t":2,"i":"O'rta Osiyo orqali"},
    ],
    "Biologiya":[
        {"s":"Fotosintez qayerda?","v":["Ildiz","Barg","Gul","Meva"],"t":1,"i":"Bargdagi xloroplastlarda"},
        {"s":"Odamda nechta suyak?","v":["186","196","206","216"],"t":2,"i":"206 ta suyak"},
        {"s":"Eng katta organ?","v":["Yurak","Jigar","Teri","O'pka"],"t":2,"i":"Teri - 2m²"},
    ],
    "Fizika":[
        {"s":"Yorug'lik tezligi (km/s)?","v":["100,000","200,000","300,000","400,000"],"t":2,"i":"c=300,000 km/s"},
        {"s":"Suv qaynash harorati?","v":["50°C","80°C","100°C","120°C"],"t":2,"i":"Normal bosimda 100°C"},
        {"s":"Nyuton 2-qonuni?","v":["F=mv","F=ma","F=ms","F=mt"],"t":1,"i":"F=ma"},
    ],
    "Kimyo":[
        {"s":"Suv formulasi?","v":["CO₂","H₂O","NaCl","O₂"],"t":1,"i":"H₂O"},
        {"s":"Mis belgisi?","v":["Co","Cu","Cr","Ca"],"t":1,"i":"Cu=Cuprum"},
        {"s":"Eng yengil element?","v":["Geliy","Vodorod","Litiy","Neon"],"t":1,"i":"H-Vodorod"},
    ],
    "Ingliz tili":[
        {"s":"Present Perfect qachon?","v":["Kecha","Hozir tugagan","Kelajak","Doim"],"t":1,"i":"Have/has+V3"},
        {"s":"'Ambitious' ma'nosi?","v":["Dangasa","Maqsadli","Qo'rqoq","Baxtli"],"t":1,"i":"Maqsadli,g'ayratli"},
    ],
    "Geografiya":[
        {"s":"O'zbekistonda nechta viloyat?","v":["10","12","14","16"],"t":2,"i":"14 ta viloyat"},
        {"s":"Eng katta okean?","v":["Atlantika","Hind","Tinch","Shimoliy"],"t":2,"i":"Tinch - 165 mln km²"},
    ],
}
YUTUQLAR = {
    "birinchi":{"nom":"🌟 Birinchi qadam","tavsif":"Birinchi javob"},
    "o10":{"nom":"🔥 10 javob","tavsif":"10 ta savol"},
    "o50":{"nom":"💪 50 javob","tavsif":"50 ta savol"},
    "o100":{"nom":"🏆 100 javob","tavsif":"100 ta savol"},
    "streak5":{"nom":"⚡ 5 streak","tavsif":"5 ketma-ket to'g'ri"},
    "streak10":{"nom":"🌊 10 streak","tavsif":"10 ketma-ket to'g'ri"},
    "ustoz":{"nom":"👨‍🏫 Ustoz","tavsif":"O'qituvchi tasdiqlandi"},
    "premium":{"nom":"💎 Premium","tavsif":"Premium oldi"},
}

DB_FILE = "zakovatbot_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {"users":{},"teachers":{},"teacher_req":{},"kesh":{},
            "stats":{"total_users":0,"total_answers":0,"total_teachers":0,"start_date":str(date.today())}}

def save_db(db):
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(db,f,ensure_ascii=False,indent=2)

def get_user(uid,ism="",username=""):
    db=load_db(); u_str=str(uid)
    if u_str not in db["users"]:
        db["users"][u_str]={"ism":ism,"username":username,"sinf":None,"ball":0,"togri":0,"notogri":0,
            "streak":0,"max_streak":0,"premium":False,"role":"student","yutuqlar":[],
            "korilgan":[],"referral":0,"ref_by":None,"qoshilgan":str(date.today()),
            "kunlik_savol":0,"kunlik_sana":str(date.today())}
        db["stats"]["total_users"]+=1; save_db(db)
    u=db["users"][u_str]
    if u.get("kunlik_sana")!=str(date.today()):
        u["kunlik_savol"]=0; u["kunlik_sana"]=str(date.today())
        db["users"][u_str]=u; save_db(db)
    return u

def update_user(uid,data):
    db=load_db(); u_str=str(uid)
    if u_str in db["users"]: db["users"][u_str].update(data); save_db(db)

def is_teacher(uid):
    db=load_db(); return db.get("teachers",{}).get(str(uid),{}).get("tasdiqlangan",False)

def get_teacher(uid):
    db=load_db(); return db.get("teachers",{}).get(str(uid),{})

def can_savol(uid):
    u=get_user(uid)
    if u.get("premium"): return True,9999
    k=u.get("kunlik_savol",0)
    if k>=BEPUL_LIMIT: return False,0
    return True,BEPUL_LIMIT-k

def can_teacher_test(uid):
    db=load_db(); t=db.get("teachers",{}).get(str(uid),{})
    if t.get("premium"): return True,9999
    bugun=t.get("bugun_test",0) if t.get("bugun_sana")==str(date.today()) else 0
    if bugun>=TEACHER_LIMIT: return False,0
    return True,TEACHER_LIMIT-bugun

def javob_berdi(uid,togri):
    db=load_db(); u_str=str(uid); u=db["users"][u_str]
    if togri: u["ball"]+=10; u["togri"]+=1; u["streak"]=u.get("streak",0)+1
    else: u["notogri"]=u.get("notogri",0)+1; u["streak"]=0
    if u["streak"]>u.get("max_streak",0): u["max_streak"]=u["streak"]
    u["kunlik_savol"]=u.get("kunlik_savol",0)+1
    db["stats"]["total_answers"]=db["stats"].get("total_answers",0)+1
    db["users"][u_str]=u; save_db(db); return u

def savol_korildi(uid,s):
    db=load_db(); u_str=str(uid)
    if u_str in db["users"]:
        if s not in db["users"][u_str].get("korilgan",[]): db["users"][u_str].setdefault("korilgan",[]).append(s)
        if len(db["users"][u_str]["korilgan"])>500: db["users"][u_str]["korilgan"]=db["users"][u_str]["korilgan"][-500:]
        save_db(db)

def check_yutuqlar(u):
    yangi=[]; mav=u.get("yutuqlar",[])
    jami=u.get("togri",0)+u.get("notogri",0)
    if jami>=1 and "birinchi" not in mav: yangi.append("birinchi")
    if jami>=10 and "o10" not in mav: yangi.append("o10")
    if jami>=50 and "o50" not in mav: yangi.append("o50")
    if jami>=100 and "o100" not in mav: yangi.append("o100")
    if u.get("streak",0)>=5 and "streak5" not in mav: yangi.append("streak5")
    if u.get("streak",0)>=10 and "streak10" not in mav: yangi.append("streak10")
    return yangi

async def groq_req(prompt,max_tokens=2000):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
                json={"model":"llama3-70b-8192","messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens,"temperature":0.7},
                timeout=aiohttp.ClientTimeout(total=30)) as r:
                if r.status==200: d=await r.json(); return d["choices"][0]["message"]["content"]
    except Exception as e: logger.error(f"Groq: {e}")
    return ""

async def get_savol(fan,sinf,uid):
    db=load_db(); k=f"{fan}_{sinf}"
    korilgan=db.get("users",{}).get(str(uid),{}).get("korilgan",[])
    kesh=db.get("kesh",{}).get(k,[])
    if len(kesh)<5:
        prompt=f"""Sen O'zbekiston {sinf}-sinf {fan} DTM test tuzuvchisan.
15 ta savol yoz, FAQAT JSON:
[{{"s":"savol","v":["A","B","C","D"],"t":0,"i":"tushuntirish"}}]
t=to'g'ri indeks(0-3), O'zbek tilida, DTM darajasida, faqat JSON"""
        resp=await groq_req(prompt)
        try:
            m=re.search(r'\[.*\]',resp,re.DOTALL)
            if m:
                ns=json.loads(m.group()); db.setdefault("kesh",{})[k]=ns[:20]; save_db(db); kesh=db["kesh"][k]
        except: pass
    if kesh:
        korilmagan=[i for i,s in enumerate(kesh) if s["s"] not in korilgan]
        if not korilmagan: update_user(uid,{"korilgan":[]}); korilmagan=list(range(len(kesh)))
        idx=random.choice(korilmagan); return kesh[idx],idx
    fn=fan.replace(" va adabiyot","").replace("Algebra","Matematika").replace("Geometriya","Matematika")
    z=ZAXIRA.get(fn,ZAXIRA.get("Matematika",[])); idx=random.randint(0,len(z)-1); return z[idx],idx

async def groq_tushuntir(savol,xato,togri,fan):
    prompt=f"""Sen {fan} DTM repetitorisin. O'quvchi xato qildi.
Savol: {savol}
Tanladi: {xato}
To'g'ri: {togri}
2-3 jumlada sodda tushuntir nima uchun {togri} to'g'ri. O'zbek tilida, faqat tushuntirish."""
    r=await groq_req(prompt,300)
    return r if r else f"To'g'ri javob: {togri}"

async def groq_test(fan,sinf,mavzu,soni,qiyinlik):
    qt={"oson":"oson (boshlang'ich)","urta":"o'rta (DTM standart)","qiyin":"qiyin (olimpiada)"}.get(qiyinlik,"o'rta")
    prompt=f"""Sen {sinf}-sinf {fan} professional test tuzuvchisan.
Mavzu: {mavzu}, Qiyinlik: {qt}, Soni: {soni}
FAQAT JSON: [{{"s":"savol","v":["A","B","C","D"],"t":0,"i":"tushuntirish"}}]
t=to'g'ri indeks, O'zbek tilida, {mavzu} mavzusiga oid, faqat JSON"""
    resp=await groq_req(prompt,4000)
    try:
        m=re.search(r'\[.*\]',resp,re.DOTALL)
        if m: return json.loads(m.group())[:soni]
    except Exception as e: logger.error(f"Test: {e}")
    return []

def pdf_oddiy(fan,sinf,mavzu,savollar,ustoz=""):
    fname=f"oddiy_{fan}_{sinf}.pdf"
    doc=SimpleDocTemplate(fname,pagesize=A4,topMargin=2*cm,bottomMargin=2*cm)
    st=getSampleStyleSheet()
    ts=ParagraphStyle("t",fontSize=15,alignment=TA_CENTER,spaceAfter=5,fontName="Helvetica-Bold")
    ss=ParagraphStyle("s",fontSize=10,alignment=TA_CENTER,spaceAfter=3)
    bs=ParagraphStyle("b",fontSize=11,spaceAfter=3,fontName="Helvetica")
    bold=ParagraphStyle("bo",fontSize=11,spaceAfter=2,fontName="Helvetica-Bold")
    story=[Paragraph(f"{fan} — {sinf}-sinf",ts),Paragraph(f"Mavzu: {mavzu}",ss)]
    if ustoz: story.append(Paragraph(f"O'qituvchi: {ustoz}",ss))
    story+=[Paragraph(f"Savollar: {len(savollar)} ta | Sana: {date.today()}",ss),
            HRFlowable(width="100%",thickness=1,color=colors.black,spaceAfter=8)]
    hrf=["A","B","C","D"]
    for i,s in enumerate(savollar):
        story.append(Paragraph(f"{i+1}. {s['s']}",bold))
        for j,v in enumerate(s["v"]): story.append(Paragraph(f"   {hrf[j]}) {v}",bs))
        story.append(Spacer(1,5))
    story+=[HRFlowable(width="100%",thickness=0.5,color=colors.grey,spaceBefore=8),
            Paragraph("Omad! | @ZakovatEduBot",ss)]
    doc.build(story); return fname

def pdf_professional(fan,sinf,mavzu,savollar,ustoz="",maktab=""):
    fname=f"pro_{fan}_{sinf}.pdf"
    ko=colors.HexColor("#1a237e"); yq=colors.HexColor("#e8eaf6")
    doc=SimpleDocTemplate(fname,pagesize=A4,topMargin=1.5*cm,bottomMargin=1.5*cm,leftMargin=2*cm,rightMargin=2*cm)
    ts=ParagraphStyle("t",fontSize=16,alignment=TA_CENTER,spaceAfter=4,fontName="Helvetica-Bold",textColor=ko)
    ss=ParagraphStyle("s",fontSize=10,alignment=TA_CENTER,spaceAfter=3)
    bs=ParagraphStyle("b",fontSize=10,spaceAfter=3)
    bold=ParagraphStyle("bo",fontSize=10,spaceAfter=2,fontName="Helvetica-Bold")
    sm=ParagraphStyle("sm",fontSize=8,alignment=TA_CENTER,textColor=colors.grey)
    story=[]
    info=[[Paragraph(f"<b>{fan} | {sinf}-sinf</b>",ParagraphStyle("",fontSize=13,fontName="Helvetica-Bold",textColor=ko)),
           Paragraph(f"<b>Mavzu: {mavzu}</b>",ParagraphStyle("",fontSize=11,fontName="Helvetica-Bold"))],
          [Paragraph(f"Maktab: {maktab or '___________'}",bs),Paragraph(f"Sana: {date.today()}",bs)],
          [Paragraph(f"O'qituvchi: {ustoz or '___________'}",bs),
           Paragraph(f"Savollar: {len(savollar)} ta | Vaqt: {len(savollar)*2} daq",bs)]]
    it=Table(info,colWidths=[8.5*cm,8.5*cm])
    it.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),yq),("GRID",(0,0),(-1,-1),0.5,colors.grey),("PADDING",(0,0),(-1,-1),6)]))
    story.append(it); story.append(Spacer(1,6))
    ot=Table([["Familiya, Ism:","___________________________________","Sinf:","_______","Ball:","_______"]],
             colWidths=[3*cm,6*cm,1.5*cm,2*cm,1.5*cm,3*cm])
    ot.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black),("PADDING",(0,0),(-1,-1),5),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
        ("BACKGROUND",(0,0),(0,0),yq),("BACKGROUND",(2,0),(2,0),yq),("BACKGROUND",(4,0),(4,0),yq)]))
    story.append(ot); story.append(Spacer(1,8))
    story.append(HRFlowable(width="100%",thickness=1.5,color=ko,spaceAfter=6))
    hrf=["A","B","C","D"]; col1=[]; col2=[]
    for i,s in enumerate(savollar):
        b=[Paragraph(f"<b>{i+1}.</b> {s['s']}",bold)]
        for j,v in enumerate(s["v"]): b.append(Paragraph(f"   <b>{hrf[j]})</b> {v}",bs))
        b.append(Spacer(1,4))
        (col1 if i%2==0 else col2).extend(b)
    if col2:
        tc=Table([[col1,col2]],colWidths=[8.5*cm,8.5*cm])
        tc.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),3)])); story.append(tc)
    else: story.extend(col1)
    story.append(PageBreak()); story.append(Paragraph("JAVOBLAR JADVALI",ts))
    story.append(HRFlowable(width="100%",thickness=1.5,color=ko,spaceAfter=8))
    rows=[["№","Javob","№","Javob","№","Javob","№","Javob","№","Javob"]]
    chunk=[savollar[i:i+5] for i in range(0,len(savollar),5)]
    for ri,ch in enumerate(chunk):
        row=[]
        for ci,s in enumerate(ch):
            row+=[str(ri*5+ci+1),hrf[s.get("t",0)]]
        while len(row)<10: row.append("")
        rows.append(row)
    jt=Table(rows,colWidths=[1*cm,2.5*cm]*5)
    jt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ko),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),("PADDING",(0,0),(-1,-1),5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f5f5f5")])]))
    story+=[jt,Spacer(1,10),Paragraph(f"ZakovatEduBot | {date.today()}",sm)]
    doc.build(story); return fname

def main_menu(premium=False,role="student"):
    btns=[[KeyboardButton("📚 O'rganish"),KeyboardButton("🏆 Reyting")],
          [KeyboardButton("👤 Profilim"),KeyboardButton("🎯 Tezkor test")],
          [KeyboardButton("👥 Do'stlar"),KeyboardButton("ℹ️ Yordam")]]
    if premium: btns.append([KeyboardButton("📄 PDF Test")])
    if role in("teacher","admin") or is_teacher(0): btns.append([KeyboardButton("👨‍🏫 O'qituvchi panel")])
    if role=="admin": btns.append([KeyboardButton("⚙️ Admin panel")])
    return ReplyKeyboardMarkup(btns,resize_keyboard=True)

def main_menu_uid(uid):
    u=get_user(uid); return main_menu(u.get("premium",False),u.get("role","student"))

def sinf_menu():
    rows=[]; row=[]
    for i in range(1,12):
        row.append(InlineKeyboardButton(f"{i}-sinf",callback_data=f"sinf_{i}"))
        if len(row)==4: rows.append(row); row=[]
    if row: rows.append(row)
    return InlineKeyboardMarkup(rows)

def fanlar_menu(sinf):
    fanlar=SINF_FANLAR.get(str(sinf),[])
    rows=[]; row=[]
    for f in fanlar:
        row.append(InlineKeyboardButton(f"{FAN_EMOJI.get(f,'📚')} {f}",callback_data=f"fan_{sinf}_{f}"))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([InlineKeyboardButton("🔙 Orqaga",callback_data="back_sinf")])
    return InlineKeyboardMarkup(rows)

def savol_kb(fan,sinf,savol,idx):
    hrf=["A","B","C","D"]
    btns=[[InlineKeyboardButton(f"{hrf[i]}) {v}",callback_data=f"j_{fan}_{sinf}_{idx}_{i}")] for i,v in enumerate(savol["v"])]
    btns.append([InlineKeyboardButton("▶️ Keyingi",callback_data=f"fan_{sinf}_{fan}"),
                 InlineKeyboardButton("📚 Fanlar",callback_data=f"sinf_{sinf}")])
    return InlineKeyboardMarkup(btns)

async def start_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; args=context.args; ref_by=None
    if args and args[0].startswith("REF"):
        try: ref_by=int(args[0].replace("REF",""))
        except: pass
    u=get_user(user.id,user.first_name,user.username or "")
    if ref_by and ref_by!=user.id and not u.get("ref_by"):
        update_user(user.id,{"ref_by":ref_by})
        db=load_db(); ruid=str(ref_by)
        if ruid in db["users"]:
            db["users"][ruid]["referral"]=db["users"][ruid].get("referral",0)+1
            db["users"][ruid]["ball"]=db["users"][ruid].get("ball",0)+20; save_db(db)
            try: await context.bot.send_message(ref_by,"🎉 Do'stingiz qo'shildi! +20 ball!")
            except: pass
    role=u.get("role","student")
    txt=(f"🎓 Xush kelibsiz, *{user.first_name}*!\nMen — *ZakovatEduBot* — AI o'qituvchingiz!\n\n"
         f"{'💎 Premium' if u.get('premium') else '🆓 Bepul'} | Sinf: {u['sinf'] or '?'} | Ball: {u['ball']}\n"
         f"Bugun: {u.get('kunlik_savol',0)}/{BEPUL_LIMIT if not u.get('premium') else '∞'} savol\n\n"
         f"1-11 sinf — CHEKSIZ AI savollar! 🚀")
    await update.message.reply_text(txt,parse_mode="Markdown",reply_markup=main_menu(u.get("premium"),role))

async def profile_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; u=get_user(user.id)
    jami=u.get("togri",0)+u.get("notogri",0); foiz=round(u["togri"]/jami*100) if jami>0 else 0
    bars="🟦"*min(foiz//10,10)+"⬜"*(10-min(foiz//10,10))
    txt=(f"👤 *{user.first_name}*\n{'💎 Premium' if u.get('premium') else '🆓 Bepul'} | "
         f"{'👨‍🏫 O\'qituvchi' if is_teacher(user.id) else '🎓 O\'quvchi'}\n\n"
         f"🏫 Sinf: {u['sinf'] or '?'}\n💎 Ball: *{u['ball']}*\n"
         f"✅ To'g'ri: {u.get('togri',0)} | ❌ Noto'g'ri: {u.get('notogri',0)}\n"
         f"📊 O'zlashtirish: {foiz}%\n{bars}\n"
         f"🔥 Streak: {u.get('streak',0)} | Max: {u.get('max_streak',0)}\n"
         f"📅 Bugun: {u.get('kunlik_savol',0)} ta\n"
         f"👥 Taklif: {u.get('referral',0)} | 🏆 Yutuq: {len(u.get('yutuqlar',[]))}/{len(YUTUQLAR)}")
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("🏆 Yutuqlar",callback_data="yutuqlar"),
        InlineKeyboardButton("↕️ Sinf o'zgartir",callback_data="sinf_ozgartir")],
        [InlineKeyboardButton("💎 Premium",callback_data="premium_info")]])
    await update.message.reply_text(txt,parse_mode="Markdown",reply_markup=kb)

async def reyting_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    db=load_db(); users=[(uid,u) for uid,u in db["users"].items() if u.get("ball",0)>0]
    users.sort(key=lambda x:x[1].get("ball",0),reverse=True); top=users[:10]
    medal=["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    uid_str=str(update.effective_user.id); txt="🏆 *TOP 10*\n\n"
    for i,(uid,u) in enumerate(top):
        me=" ← Siz" if uid==uid_str else ""
        txt+=f"{medal[i]} {u.get('ism','?')} — *{u.get('ball',0)}* ball{me}\n"
    my_pos=next((i+1 for i,(uid,_) in enumerate(users) if uid==uid_str),None)
    if my_pos and my_pos>10: txt+=f"\n📍 Sizning o'rningiz: *{my_pos}*"
    if not users: txt="🏆 *REYTING*\n\nHali hech kim yo'q! Birinchi bo'ling! 🚀"
    await update.message.reply_text(txt,parse_mode="Markdown")

async def dostlar_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; u=get_user(user.id)
    link=f"https://t.me/ZakovatEduBot?start=REF{user.id}"
    txt=(f"👥 *DO'STLARNI TAKLIF QILING!*\n\nHar do'st: *+20 ball* 🎁\n"
         f"Taklif: *{u.get('referral',0)} kishi* | Bonus: *{u.get('referral',0)*20} ball*\n\n🔗 `{link}`")
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Ulashish",
        url=f"https://t.me/share/url?url={link}&text=ZakovatEduBot+bilan+o'qiyman!")]])
    await update.message.reply_text(txt,parse_mode="Markdown",reply_markup=kb)

async def yordam_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *YORDAM*\n\n📚 O'rganish — Test ishlang\n🎯 Tezkor test — Tez boshlang\n"
        "🏆 Reyting — Top o'quvchilar\n👤 Profilim — Statistika\n"
        "👨‍🏫 O'qituvchi panel — Test yarat, PDF ol\n\n"
        "💎 *Premium:* Cheksiz savol, PDF, Statistika\n"
        "O'quvchi: 19,000 so'm/oy | O'qituvchi: 49,000 so'm/oy\n\n"
        "📞 @ZakovatHelp",parse_mode="Markdown")

async def teacher_panel_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user
    if is_teacher(user.id) or user.id==ADMIN_ID:
        t=get_teacher(user.id); can,qoldi=can_teacher_test(user.id)
        premium=t.get("premium",False) or user.id==ADMIN_ID
        txt=(f"👨‍🏫 *O'QITUVCHI PANEL*\n\nSalom, *{user.first_name}*!\n"
             f"{'💎 Premium' if premium else '🆓 Bepul'} o'qituvchi\n\n"
             f"Bugun yaratildi: {TEACHER_LIMIT-qoldi if not premium else '∞'} ta\n"
             f"Qoldi: *{qoldi if not premium else '∞'}* ta")
        kb=ReplyKeyboardMarkup([[KeyboardButton("✏️ Yangi test"),KeyboardButton("📁 Mening testlarim")],
            [KeyboardButton("📊 Statistika"),KeyboardButton("💎 Premium")],
            [KeyboardButton("🔙 Orqaga")]],resize_keyboard=True)
        await update.message.reply_text(txt,parse_mode="Markdown",reply_markup=kb)
    else:
        db=load_db(); uid=str(user.id)
        if uid in db.get("teacher_req",{}):
            await update.message.reply_text("⏳ *Arizangiz ko'rib chiqilmoqda!*",parse_mode="Markdown")
        else:
            context.user_data["teacher_ariza"]=True
            await update.message.reply_text(
                "👨‍🏫 *O'QITUVCHI PANELI*\n\nAriza berish uchun to'liq ism va maktabingizni yozing:\n"
                "_Misol: Sardor Karimov, 45-maktab, Toshkent_",parse_mode="Markdown")

async def handle_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user; txt=update.message.text
    u=get_user(user.id,user.first_name,user.username or ""); role=u.get("role","student")

    if context.user_data.get("teacher_ariza"):
        context.user_data.pop("teacher_ariza")
        db=load_db(); uid=str(user.id)
        db.setdefault("teacher_req",{})[uid]={"ism":user.first_name,"username":user.username or "","user_id":user.id,"malumot":txt,"sana":str(date.today())}
        save_db(db)
        await update.message.reply_text("✅ *Ariza qabul qilindi! Admin tez orada javob beradi.*",parse_mode="Markdown")
        if ADMIN_ID:
            try:
                await context.bot.send_message(ADMIN_ID,
                    f"👨‍🏫 *Yangi ariza!*\n👤 {user.first_name} | @{user.username or 'yoq'}\n🆔 {user.id}\n📝 {txt}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Tasdiqlash",callback_data=f"approve_{user.id}"),
                        InlineKeyboardButton("❌ Rad",callback_data=f"reject_{user.id}")]]))
            except: pass
        return

    if context.user_data.get("test_bosqich")=="mavzu":
        context.user_data["test_mavzu"]=txt; context.user_data["test_bosqich"]="qiyinlik"
        await update.message.reply_text(
            f"📚 {context.user_data.get('test_fan')} | {context.user_data.get('test_sinf')}-sinf\n📝 Mavzu: *{txt}*\n\n3️⃣ Qiyinlik:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🟢 Oson",callback_data="qiyin_oson"),
                InlineKeyboardButton("🟡 O'rta",callback_data="qiyin_urta"),
                InlineKeyboardButton("🔴 Qiyin",callback_data="qiyin_qiyin")]])); return

    if context.user_data.get("test_bosqich")=="maktab":
        context.user_data["test_maktab"]=txt if txt!="-" else ""
        await _gen_test(update,context); return

    if context.user_data.get("pdf_bosqich")=="mavzu":
        context.user_data["pdf_mavzu"]=txt; context.user_data["pdf_bosqich"]="soni"
        await update.message.reply_text(f"Mavzu: *{txt}*\n\nNechta savol?",parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("10",callback_data="pdf_soni_10"),
                InlineKeyboardButton("20",callback_data="pdf_soni_20"),
                InlineKeyboardButton("30",callback_data="pdf_soni_30")]])); return

    if txt=="📚 O'rganish":
        await update.message.reply_text("🏫 *Sinf tanlang:*",parse_mode="Markdown",reply_markup=sinf_menu())
    elif txt=="🎯 Tezkor test":
        sinf=u.get("sinf","9") or "9"; can,_=can_savol(user.id)
        if not can:
            await update.message.reply_text(f"⏰ *Limit tugadi!* ({BEPUL_LIMIT}/kun)\n💎 Premium: 19,000 so'm/oy\n@ZakovatHelp",parse_mode="Markdown"); return
        fan=random.choice(SINF_FANLAR.get(str(sinf),SINF_FANLAR["9"]))
        await update.message.reply_text("⚡ AI savol tayyorlamoqda...")
        savol,idx=await get_savol(fan,sinf,user.id)
        await update.message.reply_text(f"{FAN_EMOJI.get(fan,'📚')} *{fan}* | {sinf}-sinf\n\n*{savol['s']}*\n\nJavob:",
            parse_mode="Markdown",reply_markup=savol_kb(fan,str(sinf),savol,idx))
    elif txt=="🏆 Reyting": await reyting_cmd(update,context)
    elif txt=="👤 Profilim": await profile_cmd(update,context)
    elif txt=="👥 Do'stlar": await dostlar_cmd(update,context)
    elif txt=="ℹ️ Yordam": await yordam_cmd(update,context)
    elif txt=="👨‍🏫 O'qituvchi panel": await teacher_panel_cmd(update,context)
    elif txt=="✏️ Yangi test":
        if not is_teacher(user.id) and user.id!=ADMIN_ID: return
        can,qoldi=can_teacher_test(user.id)
        if not can:
            await update.message.reply_text(f"❌ Kunlik limit! ({TEACHER_LIMIT}/kun)\n💎 Premium: 49,000 so'm/oy",parse_mode="Markdown"); return
        context.user_data["test_bosqich"]="sinf"
        await update.message.reply_text("✏️ *YANGI TEST*\n\n1️⃣ Sinf tanlang:",parse_mode="Markdown",reply_markup=sinf_menu())
    elif txt=="📁 Mening testlarim":
        if not is_teacher(user.id) and user.id!=ADMIN_ID: return
        db=load_db(); t=db.get("teachers",{}).get(str(user.id),{}); tl=t.get("testlar",[])
        if not tl: await update.message.reply_text("📁 Hali test yo'q!"); return
        res="📁 *MENING TESTLARIM*\n\n"
        for i,ti in enumerate(tl[-10:]):
            res+=f"{i+1}. {ti.get('fan')} | {ti.get('sinf')}-sinf | {ti.get('soni')} ta | {ti.get('sana')}\n"
        await update.message.reply_text(res,parse_mode="Markdown")
    elif txt=="📊 Statistika":
        if not is_teacher(user.id) and user.id!=ADMIN_ID: return
        db=load_db(); t=db.get("teachers",{}).get(str(user.id),{})
        await update.message.reply_text(
            f"📊 *STATISTIKA*\n\nJami testlar: {len(t.get('testlar',[]))}\nBugun: {t.get('bugun_test',0)} ta",parse_mode="Markdown")
    elif txt in("💎 Premium","💎 Premium olish"):
        await update.message.reply_text(
            "💎 *PREMIUM*\n\n👨‍🎓 O'quvchi: 39,000 so'm/oy\n• Cheksiz savol\n• PDF test\n\n"
            "👨‍🏫 O'qituvchi: 79,000 so'm/oy\n• Cheksiz test\n• Professional PDF (40-50 savol)\n\n📞 @ZakovatHelp",parse_mode="Markdown")
    elif txt=="🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu:",reply_markup=main_menu_uid(user.id))
    elif txt=="📄 PDF Test":
        if not u.get("premium") and user.id!=ADMIN_ID:
            await update.message.reply_text("💎 Bu Premium uchun!\n39,000 so'm/oy | @ZakovatHelp"); return
        context.user_data["pdf_bosqich"]="sinf"
        await update.message.reply_text("📄 *PDF Test — Sinf:*",parse_mode="Markdown",reply_markup=sinf_menu())
    elif txt=="⚙️ Admin panel":
        if user.id!=ADMIN_ID: return
        db=load_db(); reqs=db.get("teacher_req",{})
        txt2=(f"⚙️ *ADMIN*\n👥 Foydalanuvchi: {db['stats'].get('total_users',0)}\n"
              f"📊 Javoblar: {db['stats'].get('total_answers',0)}\n"
              f"👨‍🏫 O'qituvchilar: {len(db.get('teachers',{}))}\n⏳ Arizalar: {len(reqs)}")
        btns=[]
        if reqs: btns.append([InlineKeyboardButton(f"👨‍🏫 Arizalar ({len(reqs)})",callback_data="admin_arizalar")])
        await update.message.reply_text(txt2,parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(btns) if btns else None)
    else:
        await update.message.reply_text("Tugmalardan foydalaning! 👇",reply_markup=main_menu_uid(user.id))

async def _gen_test(update,context):
    user=update.effective_user
    fan=context.user_data.get("test_fan","Matematika"); sinf=context.user_data.get("test_sinf","9")
    mavzu=context.user_data.get("test_mavzu","Umumiy"); qiyinlik=context.user_data.get("test_qiyinlik","urta")
    soni=context.user_data.get("test_soni",20); pdf_tur=context.user_data.get("test_pdf_tur","pro")
    maktab=context.user_data.get("test_maktab","")
    await update.message.reply_text(
        f"⏳ *AI test yaratyapti...*\n📚 {fan} | {sinf}-sinf\n📝 {mavzu}\n{soni} ta | {QIYINLIK_NOMI.get(qiyinlik,qiyinlik)}\n_30-60 soniya..._",
        parse_mode="Markdown")
    savollar=await groq_test(fan,sinf,mavzu,soni,qiyinlik)
    if not savollar:
        fn=fan.replace(" va adabiyot","").replace("Algebra","Matematika")
        savollar=ZAXIRA.get(fn,ZAXIRA.get("Matematika",[]))
    try:
        t=get_teacher(user.id); ustoz=t.get("ism",user.first_name) or user.first_name
        pf=pdf_professional(fan,sinf,mavzu,savollar,ustoz,maktab) if pdf_tur=="pro" else pdf_oddiy(fan,sinf,mavzu,savollar,ustoz)
        with open(pf,"rb") as f:
            await context.bot.send_document(chat_id=user.id,document=f,
                filename=f"Test_{fan}_{sinf}sinf.pdf",
                caption=f"✅ *Test tayyor!*\n📚 {fan} | {sinf}-sinf\n📝 {mavzu}\n❓ {len(savollar)} ta | {QIYINLIK_NOMI.get(qiyinlik,qiyinlik)}",
                parse_mode="Markdown")
        os.remove(pf)
        db=load_db(); uid=str(user.id)
        if uid in db.get("teachers",{}):
            if db["teachers"][uid].get("bugun_sana")!=str(date.today()): db["teachers"][uid]["bugun_test"]=0; db["teachers"][uid]["bugun_sana"]=str(date.today())
            db["teachers"][uid]["bugun_test"]=db["teachers"][uid].get("bugun_test",0)+1
            db["teachers"][uid].setdefault("testlar",[]).append({"fan":fan,"sinf":sinf,"mavzu":mavzu,"soni":len(savollar),"sana":str(date.today())})
            save_db(db)
    except Exception as e: logger.error(f"PDF: {e}"); await context.bot.send_message(user.id,"❌ PDF xatosi!")
    context.user_data.clear()

async def handle_callback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); data=q.data; user=update.effective_user
    u=get_user(user.id,user.first_name,user.username or "")

    if data.startswith("approve_") and user.id==ADMIN_ID:
        tid=int(data.replace("approve_","")); db=load_db(); uid=str(tid)
        req=db.get("teacher_req",{}).get(uid,{})
        db.setdefault("teachers",{})[uid]={"ism":req.get("ism",""),"username":req.get("username",""),"user_id":tid,
            "tasdiqlangan":True,"premium":False,"testlar":[],"bugun_test":0,"bugun_sana":str(date.today()),"qoshilgan":str(date.today())}
        db.get("teacher_req",{}).pop(uid,None); save_db(db)
        await q.edit_message_text(f"✅ {req.get('ism',uid)} tasdiqlandi!")
        try: await context.bot.send_message(tid,"🎉 *Tabrik! O'qituvchi sifatida tasdiqlandi!*\n👨‍🏫 O'qituvchi panel → ✏️ Yangi test",parse_mode="Markdown")
        except: pass

    elif data.startswith("reject_") and user.id==ADMIN_ID:
        tid=int(data.replace("reject_","")); db=load_db()
        db.get("teacher_req",{}).pop(str(tid),None); save_db(db)
        await q.edit_message_text("❌ Rad etildi.")
        try: await context.bot.send_message(tid,"❌ Arizangiz rad etildi. @ZakovatSupport")
        except: pass

    elif data=="admin_arizalar" and user.id==ADMIN_ID:
        db=load_db(); reqs=db.get("teacher_req",{})
        if not reqs: await q.edit_message_text("Ariza yo'q!"); return
        txt="👨‍🏫 *ARIZALAR*\n\n"; btns=[]
        for uid,req in list(reqs.items())[:10]:
            txt+=f"👤 {req.get('ism')} | {req.get('malumot','')[:40]}\n"
            btns.append([InlineKeyboardButton(f"✅ {req.get('ism')}",callback_data=f"approve_{uid}"),
                         InlineKeyboardButton("❌",callback_data=f"reject_{uid}")])
        await q.edit_message_text(txt,parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("sinf_") and not data.startswith("sinf_ozgartir"):
        sinf=data.replace("sinf_","")
        if sinf.isdigit():
            if context.user_data.get("test_bosqich")=="sinf":
                context.user_data["test_sinf"]=sinf; context.user_data["test_bosqich"]="fan"
                await q.edit_message_text(f"✏️ *YANGI TEST*\n🏫 Sinf: {sinf}\n\n2️⃣ Fan:",parse_mode="Markdown",reply_markup=fanlar_menu(sinf))
            elif context.user_data.get("pdf_bosqich")=="sinf":
                context.user_data["pdf_sinf"]=sinf; context.user_data["pdf_bosqich"]="fan"
                await q.edit_message_text(f"Sinf: *{sinf}*\nFan:",parse_mode="Markdown",reply_markup=fanlar_menu(sinf))
            else:
                update_user(user.id,{"sinf":sinf})
                await q.edit_message_text(f"*{sinf}-sinf tanlandi!*\nQaysi fan?",parse_mode="Markdown",reply_markup=fanlar_menu(sinf))

    elif data in("sinf_ozgartir","back_sinf"):
        await q.edit_message_text("*Sinf tanlang:*",parse_mode="Markdown",reply_markup=sinf_menu())

    elif data.startswith("fan_"):
        parts=data.split("_",2)
        if len(parts)==3:
            _,sinf,fan=parts
            if context.user_data.get("test_bosqich")=="fan":
                context.user_data["test_fan"]=fan; context.user_data["test_bosqich"]="mavzu"
                await q.edit_message_text(f"✏️ *YANGI TEST*\n🏫 {sinf}-sinf | 📚 {fan}\n\n📝 Mavzuni yozing:\n_Misol: Kvadrat tenglamalar_",parse_mode="Markdown")
            elif context.user_data.get("pdf_bosqich")=="fan":
                context.user_data["pdf_fan"]=fan; context.user_data["pdf_bosqich"]="mavzu"
                await q.edit_message_text(f"Fan: *{fan}*\nMavzu yozing:",parse_mode="Markdown")
            else:
                can,_=can_savol(user.id)
                if not can: await q.edit_message_text(f"⏰ Limit! ({BEPUL_LIMIT}/kun)\n💎 Premium: 19,000 so'm\n@ZakovatSupport"); return
                await q.edit_message_text("⚡ AI savol tayyorlamoqda...")
                savol,idx=await get_savol(fan,sinf,user.id)
                await q.edit_message_text(f"{FAN_EMOJI.get(fan,'📚')} *{fan}* | {sinf}-sinf\n\n*{savol['s']}*\n\nJavob:",
                    parse_mode="Markdown",reply_markup=savol_kb(fan,sinf,savol,idx))

    elif data.startswith("j_"):
        parts=data.split("_"); fan=parts[1]; sinf=parts[2]; idx=int(parts[3]); tanlagan=int(parts[4])
        db=load_db(); k=f"{fan}_{sinf}"; kesh=db.get("kesh",{}).get(k,[])
        if not kesh or idx>=len(kesh):
            fn=fan.replace(" va adabiyot","").replace("Algebra","Matematika").replace("Geometriya","Matematika")
            kesh=ZAXIRA.get(fn,ZAXIRA.get("Matematika",[]))
        savol=kesh[idx] if idx<len(kesh) else kesh[0]; togri=savol["t"]
        hrf=["A","B","C","D"]; uu=javob_berdi(user.id,tanlagan==togri); savol_korildi(user.id,savol["s"])
        bonus=0
        if tanlagan==togri:
            if uu["streak"]==5: bonus=5; update_user(user.id,{"ball":uu["ball"]+5})
            elif uu["streak"]==10: bonus=10; update_user(user.id,{"ball":uu["ball"]+10})
        yy=check_yutuqlar(uu)
        if yy:
            db2=load_db(); db2["users"][str(user.id)]["yutuqlar"].extend(yy); save_db(db2)
        if tanlagan==togri:
            res=(f"✅ *TO'G'RI!* +10 ball"
                 +(f"\n🔥 Streak: {uu['streak']}" if uu["streak"]>1 else "")
                 +(f"\n🎁 Bonus: +{bonus}!" if bonus else "")
                 +f"\n\n💡 {savol['i']}\n\n💎 Ball: *{uu['ball']}*")
        else:
            await q.edit_message_text(
                f"❌ *NOTO'G'RI!*\nSiz: {hrf[tanlagan]}) {savol['v'][tanlagan]}\nTo'g'ri: {hrf[togri]}) *{savol['v'][togri]}*\n\n🤖 _AI tushuntiryapti..._",
                parse_mode="Markdown")
            tush=await groq_tushuntir(savol["s"],savol["v"][tanlagan],savol["v"][togri],fan)
            res=(f"❌ *NOTO'G'RI!*\nSiz: {hrf[tanlagan]}) {savol['v'][tanlagan]}\n"
                 f"To'g'ri: {hrf[togri]}) *{savol['v'][togri]}*\n\n🤖 *AI Repetitor:*\n{tush}")
        for y in yy: res+=f"\n\n🏆 *{YUTUQLAR[y]['nom']}*!"
        await q.edit_message_text(res,parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("▶️ Keyingi",callback_data=f"fan_{sinf}_{fan}"),
                InlineKeyboardButton("📚 Fanlar",callback_data=f"sinf_{sinf}")]]))

    elif data=="yutuqlar":
        mav=u.get("yutuqlar",[]); t="🏆 *YUTUQLAR*\n\n"
        for k,v in YUTUQLAR.items(): t+=f"{'✅' if k in mav else '🔒'} {v['nom']} — _{v['tavsif']}_\n"
        await q.edit_message_text(t,parse_mode="Markdown")

    elif data=="premium_info":
        await q.edit_message_text("💎 *PREMIUM*\n\nO'quvchi: 39,000 so'm/oy\nO'qituvchi: 79,000 so'm/oy\n\n📞 @ZakovatSupport",parse_mode="Markdown")

    elif data.startswith("qiyin_"):
        q_val=data.replace("qiyin_",""); context.user_data["test_qiyinlik"]=q_val; context.user_data["test_bosqich"]="soni"
        await q.edit_message_text(
            f"📚 {context.user_data.get('test_fan')} | {context.user_data.get('test_sinf')}-sinf\n"
            f"📝 {context.user_data.get('test_mavzu')} | {QIYINLIK_NOMI.get(q_val,q_val)}\n\n4️⃣ Nechta savol?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("10",callback_data="soni_10"),InlineKeyboardButton("20",callback_data="soni_20"),
                InlineKeyboardButton("30",callback_data="soni_30")],[
                InlineKeyboardButton("40 (Premium)",callback_data="soni_40"),InlineKeyboardButton("50 (Premium)",callback_data="soni_50")]]))

    elif data.startswith("soni_"):
        soni=int(data.replace("soni_","")); t=get_teacher(user.id)
        if soni>30 and not t.get("premium") and user.id!=ADMIN_ID:
            await q.edit_message_text("❌ 30+ savol faqat Premium!\n💎 49,000 so'm/oy | @ZakovatSupport"); return
        context.user_data["test_soni"]=soni; context.user_data["test_bosqich"]="pdf_tur"
        await q.edit_message_text("5️⃣ PDF turi:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📄 Oddiy",callback_data="pdf_tur_oddiy"),
                InlineKeyboardButton("🏫 Professional",callback_data="pdf_tur_pro")]]))

    elif data.startswith("pdf_tur_"):
        tur=data.replace("pdf_tur_",""); context.user_data["test_pdf_tur"]=tur
        if tur=="pro":
            context.user_data["test_bosqich"]="maktab"
            await q.edit_message_text("🏫 Maktab nomini yozing:\n_(Bo'sh qoldirish uchun - deb yozing)_",parse_mode="Markdown")
        else:
            context.user_data["test_bosqich"]="generate"; context.user_data["test_maktab"]=""
            msg=await context.bot.send_message(user.id,"⏳ Tayyorlanmoqda...")
            class FakeUpdate:
                def __init__(self,m,u): self.message=m; self.effective_user=u
            await _gen_test(FakeUpdate(msg,user),context)

    elif data.startswith("pdf_soni_"):
        soni=int(data.replace("pdf_soni_","")); fan=context.user_data.get("pdf_fan","Tarix")
        sinf=context.user_data.get("pdf_sinf","7"); mavzu=context.user_data.get("pdf_mavzu","Umumiy")
        await q.edit_message_text("⏳ PDF tayyorlanmoqda...")
        savollar=await groq_test(fan,sinf,mavzu,soni,"urta")
        if not savollar:
            fn=fan.replace(" va adabiyot","").replace("Algebra","Matematika")
            savollar=ZAXIRA.get(fn,ZAXIRA.get("Matematika",[]))
        try:
            pf=pdf_professional(fan,sinf,mavzu,savollar,u.get("ism",""))
            with open(pf,"rb") as f:
                await context.bot.send_document(chat_id=user.id,document=f,
                    filename=f"Test_{fan}_{sinf}sinf.pdf",
                    caption=f"*{fan} | {sinf}-sinf | {mavzu}*\n{len(savollar)} ta savol",parse_mode="Markdown")
            os.remove(pf); context.user_data.clear()
        except Exception as e: logger.error(f"PDF: {e}"); await context.bot.send_message(user.id,"❌ PDF xatosi!")

def main():
    print("="*50); print("  ZAKOVATBOT v3.0"); print("="*50)
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd))
    app.add_handler(CommandHandler("help",yordam_cmd))
    app.add_handler(CommandHandler("profile",profile_cmd))
    app.add_handler(CommandHandler("reyting",reyting_cmd))
    app.add_handler(CommandHandler("dostlar",dostlar_cmd))
    app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ Bot ishlayapti!"); app.run_polling(drop_pending_updates=True)

if __name__=="__main__": main()
