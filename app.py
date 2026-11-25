import os
import sqlite3
from functools import wraps
from flask import Flask, request, render_template_string, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cyberbee-secret-key-2077")

ADMIN_LOGIN = "mouf756"
ADMIN_PASS = "dae7d1f2"


def get_db():
    conn = sqlite3.connect("honey.db")
    conn.row_factory = sqlite3.Row
    return conn


def write_log(actor, action):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO logs (actor, action) VALUES (?, ?)", (actor, action))
    conn.commit()
    conn.close()


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  contact TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS zakazy
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  imya TEXT,
                  telefon TEXT,
                  tovar TEXT,
                  kolvo INTEGER,
                  summa INTEGER,
                  paid INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  actor TEXT,
                  action TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("auth_page"))
        return f(*args, **kwargs)
    return decorated


init_db()

tovary = [
    {
        "id": "alp",
        "kod": "ALP-2000 // X1",
        "paseka": "ПАСЕКА «ПИК ЭДЕЛЬВЕЙС» (2140М)",
        "nazvanie": "АЛЬПИЙСКИЙ СИНТЕЗ",
        "kratko": "Высокогорный нектар с альпийских лугов. Концентрат диких трав и горных энзимов.",
        "polnoe": "Собран автономными роями на высоте более 2000 метров над уровнем моря в изолированных альпийских долинах. Обладает насыщенным терпким ароматом горного разнотравья.",
        "cena": 1500,
        "ves": "500 Г",
        "bju": {"b": "0.8 г", "j": "0.0 г", "u": "81.5 г", "kcal": "328 ккал"},
        "svoystva": "Повышает выносливость, ускоряет восстановление после физических и умственных нагрузок, обладает природным антисептическим действием.",
        "usloviya": "Утром натощак за 20 минут до еды по 1–2 чайные ложки, запивая тёплой водой (не выше 40°C).",
        "s_chem": "Травяной горный чай, выдержанные твёрдые сыры, грецкие орехи, цельнозерновые тосты.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <polygon points="40,4 74,23 74,57 40,76 6,57 6,23" fill="rgba(255,183,0,0.08)" stroke="#ffb700" stroke-width="2"/>
            <polygon points="18,54 36,24 47,42 56,30 64,54" fill="none" stroke="#00f3ff" stroke-width="2.2"/>
            <circle cx="54" cy="19" r="4" fill="#ffb700"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 92, "ИММУНИТЕТ": 85, "РЕДКОСТЬ": 78},
    },
    {
        "id": "blond",
        "kod": "BLOND-BEE // V2",
        "paseka": "БИО-ПАСЕКА «БЕЛОЕ ЗОЛОТО»",
        "nazvanie": "НЕКТАР БЕЛОКУРЫХ ПЧЁЛ",
        "kratko": "Эксклюзивный светлый крио-крем от редкой популяции белокурых горных пчёл.",
        "polnoe": "Редчайший сорт с перламутровым отливом и нежной кремовой текстурой. Добывается закрытой популяцией светлых высокогорных пчёл.",
        "cena": 2200,
        "ves": "500 Г",
        "bju": {"b": "0.6 г", "j": "0.0 г", "u": "82.4 г", "kcal": "332 ккал"},
        "svoystva": "Мягко тонизирует нервную систему, улучшает качество сна и концентрацию внимания, не вызывает резких скачков сахара.",
        "usloviya": "Днём в период высокой умственной активности или за 40 минут до сна для восстановления нейро-баланса.",
        "s_chem": "Свежие ягоды (голубика, малина), мягкий творог, рикотта, тёплое миндальное молоко, круассаны.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <circle cx="40" cy="40" r="34" fill="rgba(0,243,255,0.06)" stroke="#00f3ff" stroke-width="2" stroke-dasharray="6 3"/>
            <polygon points="40,16 54,40 40,64 26,40" fill="rgba(255,183,0,0.25)" stroke="#ffb700" stroke-width="2.2"/>
            <circle cx="40" cy="40" r="6" fill="#fff"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 88, "ИММУНИТЕТ": 95, "РЕДКОСТЬ": 99},
    },
    {
        "id": "prop",
        "kod": "PROPOLIS // MAX",
        "paseka": "ПАСЕКА «КВАРЦЕВЫЙ УЛЕЙ»",
        "nazvanie": "КИБЕР-ПРОПОЛИС GOLD",
        "kratko": "Альпийский сбор, обогащённый концентрированным прополисом и маточным молочком.",
        "polnoe": "Синтез высокогорного мёда и очищенного экстракта прополиса. Мощный биологический щит в сезон простуд и высоких нагрузок.",
        "cena": 1800,
        "ves": "500 Г",
        "bju": {"b": "1.1 г", "j": "0.2 г", "u": "79.8 г", "kcal": "325 ккал"},
        "svoystva": "Сильнейший природный иммуномодулятор, подавляет воспалительные процессы, защищает слизистую горла и ЖКТ.",
        "usloviya": "При первых признаках усталости или переохлаждения — по 1 чайной ложке медленно рассасывать во рту 2 раза в день.",
        "s_chem": "Имбирный напиток с лимоном, облепиховый морс, печёные яблоки, овсяная каша.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <polygon points="40,6 68,18 64,52 40,74 16,52 12,18" fill="rgba(255,106,0,0.12)" stroke="#ff6a00" stroke-width="2.2"/>
            <line x1="40" y1="22" x2="40" y2="54" stroke="#00f3ff" stroke-width="3"/>
            <line x1="24" y1="38" x2="56" y2="38" stroke="#00f3ff" stroke-width="3"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 84, "ИММУНИТЕТ": 100, "РЕДКОСТЬ": 86},
    },
    {
        "id": "cedar",
        "kod": "CEDAR-RESIN // S4",
        "paseka": "ПАСЕКА «ЛЕДЯНОЙ КЕДР»",
        "nazvanie": "КЕДРОВО-ХВОЙНЫЙ НЕКТАР",
        "kratko": "Тёмный смолистый мёд с альпийской живицей и пыльцой горной сосны.",
        "polnoe": "Собирается на границе альпийских хвойных лесов. Отличается глубоким янтарно-шоколадным цветом и лёгкой хвойной горчинкой.",
        "cena": 1950,
        "ves": "500 Г",
        "bju": {"b": "0.9 г", "j": "0.1 г", "u": "80.2 г", "kcal": "326 ккал"},
        "svoystva": "Очищает дыхательную систему, богат фитонцидами и минералами (магний, калий, железо).",
        "usloviya": "После тренировок, прогулок на холоде или при работе в загазованном мегаполисе — 1 столовая ложка днём.",
        "s_chem": "Кедровые орехи, ржаной хлеб, запечённая тыква, чёрный кофе без сахара.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <rect x="12" y="12" width="56" height="56" rx="8" fill="rgba(0,243,255,0.06)" stroke="#ffb700" stroke-width="2"/>
            <polygon points="40,16 58,42 47,42 62,62 18,62 33,42 22,42" fill="none" stroke="#00f3ff" stroke-width="2"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 90, "ИММУНИТЕТ": 94, "РЕДКОСТЬ": 89},
    },
    {
        "id": "amber",
        "kod": "AMBER-SUN // R5",
        "paseka": "ПАСЕКА «ЯНТАРНЫЙ КАНЬОН»",
        "nazvanie": "ДИКИЙ ГОРНЫЙ КАШТАН",
        "kratko": "Терпкий тёмный нектар с альпийских склонов с минимальной сладостью.",
        "polnoe": "Элитный монофлорный мёд из соцветий высокогорного каштана. Практически не кристаллизуется и ценится гурманами за благородную горчинку.",
        "cena": 2100,
        "ves": "500 Г",
        "bju": {"b": "1.2 г", "j": "0.0 г", "u": "78.9 г", "kcal": "320 ккал"},
        "svoystva": "Укрепляет стенки сосудов, нормализует кровообращение и работу сердца, улучшает пищеварение.",
        "usloviya": "Во время обеда или ужина в составе гастрономических сочетаний, либо по 1 ложке после плотной еды.",
        "s_chem": "Сыр с голубой плесенью, пармезан, жареный фундук, запечённая груша, руккола.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <polygon points="40,5 75,40 40,75 5,40" fill="rgba(255,183,0,0.08)" stroke="#ff6a00" stroke-width="2.2"/>
            <circle cx="40" cy="40" r="14" fill="none" stroke="#ffb700" stroke-width="2.5"/>
            <circle cx="40" cy="40" r="4" fill="#00f3ff"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 87, "ИММУНИТЕТ": 91, "РЕДКОСТЬ": 93},
    },
    {
        "id": "royal",
        "kod": "ROYAL-JELLY // Z9",
        "paseka": "ПАСЕКА «НЕКТАРНЫЙ ОЛИМП»",
        "nazvanie": "МАТОЧНЫЙ ЭЛИКСИР БЕЛОКУРЫХ",
        "kratko": "Ультра-концентрат мёда белокурых пчёл с нативным маточным молочком.",
        "polnoe": "Флагманский био-продукт CYBERBEE. Соединяет редчайший светлый нектар белокурых пчёл и свежее маточное молочко в пропорции максимальной биодоступности.",
        "cena": 2650,
        "ves": "350 Г",
        "bju": {"b": "2.4 г", "j": "0.4 г", "u": "77.5 г", "kcal": "323 ккал"},
        "svoystva": "Мощный клеточный регенератор: ускоряет обмен веществ, повышает уровень жизненных сил и стрессоустойчивость.",
        "usloviya": "Строго в первой половине дня (до 15:00) по 1 кофейной ложке под язык, хранить в холодильнике.",
        "s_chem": "Употреблять самостоятельно в чистом виде или с прохладным смузи из банана и шпината.",
        "svg_logo": """<svg viewBox="0 0 80 80" width="56" height="56">
            <polygon points="40,4 73,22 73,58 40,76 7,58 7,22" fill="rgba(0,243,255,0.08)" stroke="#00f3ff" stroke-width="2"/>
            <polygon points="22,52 22,30 33,40 40,24 47,40 58,30 58,52" fill="none" stroke="#ffb700" stroke-width="2.4"/>
        </svg>""",
        "stats": {"ЭНЕРГИЯ": 99, "ИММУНИТЕТ": 98, "РЕДКОСТЬ": 100},
    },
]

base_style = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    :root {
        --neon-gold: #ffb700;
        --neon-amber: #ff6a00;
        --neon-cyan: #00f3ff;
        --bg-dark: #06060a;
        --panel-bg: rgba(14, 14, 24, 0.92);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
        max-width: 100%;
        overflow-x: hidden;
    }
    body {
        font-family: 'Rajdhani', sans-serif;
        background-color: var(--bg-dark);
        color: #e0e0e0;
        min-height: 100vh;
        background-image:
            radial-gradient(circle at 50% 0%, rgba(255, 183, 0, 0.16) 0%, transparent 55%),
            linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
    }
    #cursor-glow {
        position: fixed;
        width: 420px;
        height: 420px;
        border-radius: 50%;
        pointer-events: none;
        z-index: -1;
        transform: translate(-50%, -50%);
        background: radial-gradient(circle, rgba(255, 183, 0, 0.16) 0%, rgba(0, 243, 255, 0.07) 38%, transparent 70%);
    }
    .hex-bg {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: -2; opacity: 0.25;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100' viewBox='0 0 56 100'%3E%3Cpath d='M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100' fill='none' stroke='%23ffb700' stroke-width='1'/%3E%3Cpath d='M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34' fill='none' stroke='%2300f3ff' stroke-width='0.5'/%3E%3C/svg%3E");
        animation: hexMove 28s linear infinite;
    }
    @keyframes hexMove { 0% { background-position: 0 0; } 100% { background-position: 56px 100px; } }
    .smart-bee {
        position: fixed;
        width: 14px;
        height: 8px;
        background: var(--neon-gold);
        border-radius: 50%;
        box-shadow: 0 0 12px var(--neon-gold), 0 0 22px var(--neon-amber);
        pointer-events: none;
        z-index: 5;
        will-change: transform;
    }
    .smart-bee::before, .smart-bee::after {
        content: '';
        position: absolute;
        top: -5px;
        left: 3px;
        width: 6px;
        height: 10px;
        background: var(--neon-cyan);
        border-radius: 50%;
        opacity: 0.85;
        animation: wingFlap 0.07s infinite alternate;
    }
    .smart-bee::after { top: 3px; }
    @keyframes wingFlap { 0% { transform: scaleY(1); } 100% { transform: scaleY(0.2); } }

    header {
        padding: 20px 14px 16px;
        border-bottom: 1px solid rgba(255, 183, 0, 0.35);
        background: linear-gradient(180deg, rgba(255,183,0,0.1) 0%, rgba(6,6,10,0.95) 100%);
        text-align: center;
        position: relative;
        z-index: 10;
    }
    .brand-box {
        display: inline-flex; align-items: center; justify-content: center; gap: 14px;
        cursor: pointer; transition: 0.3s; text-decoration: none;
    }
    .bee-logo-svg {
        width: 56px; height: 56px;
        filter: drop-shadow(0 0 12px var(--neon-gold));
        transition: all 0.35s ease;
    }
    .logo-wing { transform-origin: 50px 45px; animation: logoWingPulse 2.5s infinite ease-in-out; }
    @keyframes logoWingPulse { 0%, 100% { opacity: 0.85; transform: scale(1); } 50% { opacity: 1; transform: scale(1.06); } }
    .brand-text { text-align: left; }
    .sys-tag { font-family: 'Orbitron', sans-serif; font-size: 9px; letter-spacing: 2px; color: var(--neon-cyan); display: block; margin-bottom: 2px; }
    h1 {
        font-family: 'Orbitron', sans-serif; font-size: clamp(24px, 6vw, 48px); font-weight: 900;
        text-transform: uppercase; color: #fff; text-shadow: 0 0 15px var(--neon-gold), 0 0 30px var(--neon-amber);
        letter-spacing: 3px; line-height: 1;
    }
    h1 span { color: var(--neon-gold); }

    .nav-bar {
        display: flex; justify-content: center; flex-wrap: wrap; gap: 8px;
        margin-top: 16px; padding: 0 4px;
    }
    .tab-btn, .nav-link {
        position: relative; padding: 10px 14px; background: rgba(15, 15, 25, 0.92);
        border: 1px solid rgba(255, 183, 0, 0.4); color: #ccc; text-decoration: none;
        font-family: 'Orbitron', sans-serif; font-size: 10px; font-weight: 700;
        letter-spacing: 1px; text-transform: uppercase; cursor: pointer;
        clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
        transition: all 0.25s ease;
        white-space: nowrap;
    }
    .tab-btn:hover, .nav-link:hover {
        border-color: var(--neon-cyan); color: var(--neon-cyan);
    }
    .tab-btn.active, .nav-link.active-page {
        background: linear-gradient(45deg, var(--neon-amber), var(--neon-gold));
        color: #050508; border-color: var(--neon-gold);
        box-shadow: 0 0 18px rgba(255, 183, 0, 0.55);
    }

    /* Мобильная сетка вкладок каталога */
    .sub-tabs {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 8px;
        margin-bottom: 22px;
    }
    .sub-tabs .tab-btn {
        width: 100%;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        padding: 10px 10px;
        font-size: 10px;
    }

    .container { width: 94%; max-width: 1220px; margin: 22px auto 50px; position: relative; z-index: 10; }
    .tab-content { display: none; animation: tabFadeIn 0.35s ease; }
    .tab-content.active { display: block; }
    @keyframes tabFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .section-title {
        font-family: 'Orbitron', sans-serif; font-size: clamp(15px, 4vw, 20px); color: var(--neon-gold);
        margin-bottom: 18px; display: flex; align-items: center; gap: 12px; text-transform: uppercase;
    }
    .section-title::after { content: ''; height: 2px; flex-grow: 1; background: linear-gradient(90deg, var(--neon-gold), transparent); }
    .katalog { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .kartochka {
        background: var(--panel-bg); border: 1px solid rgba(255, 183, 0, 0.4);
        padding: 20px; position: relative;
        clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px));
        transition: all 0.3s ease; backdrop-filter: blur(10px);
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kartochka:hover { border-color: var(--neon-cyan); box-shadow: 0 10px 28px rgba(0, 243, 255, 0.18); }
    .card-top { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .honey-logo-wrap { flex-shrink: 0; }
    .item-code { font-family: 'Orbitron', sans-serif; font-size: 9px; color: var(--neon-cyan); letter-spacing: 1px; }
    .paseka-tag { font-family: 'Orbitron', sans-serif; font-size: 10px; color: var(--neon-gold); margin-top: 2px; }
    .kartochka h3 { font-family: 'Orbitron', sans-serif; font-size: 17px; color: #fff; margin-bottom: 8px; }
    .kartochka p { font-size: 15px; line-height: 1.45; color: #b4b4cc; margin-bottom: 12px; }
    .bju-mini {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px;
        background: rgba(0, 243, 255, 0.05); border: 1px solid rgba(0, 243, 255, 0.25);
        padding: 7px; margin-bottom: 12px; text-align: center;
    }
    .bju-mini div span { display: block; font-family: 'Orbitron', sans-serif; font-size: 8px; color: var(--neon-cyan); }
    .bju-mini div strong { font-size: 12px; color: #fff; }
    .info-snippet {
        font-size: 14px; color: #d0d0e0; background: rgba(255, 183, 0, 0.05);
        border-left: 2px solid var(--neon-gold); padding: 7px 10px; margin-bottom: 12px; line-height: 1.4;
    }
    .info-snippet strong { color: var(--neon-gold); font-family: 'Orbitron', sans-serif; font-size: 9px; letter-spacing: 1px; display: block; }
    .card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 12px; }
    .ves-badge { background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); padding: 4px 8px; font-family: 'Orbitron', sans-serif; font-size: 11px; }
    .cena { font-family: 'Orbitron', sans-serif; font-size: 21px; font-weight: 900; color: var(--neon-gold); }
    .card-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; }
    .btn-outline {
        padding: 10px 8px; background: transparent; border: 1px solid var(--neon-cyan);
        color: var(--neon-cyan); font-family: 'Orbitron', sans-serif; font-size: 10px;
        font-weight: 700; cursor: pointer; text-transform: uppercase;
    }
    .btn-outline:hover { background: var(--neon-cyan); color: #000; }
    .btn-fill {
        padding: 10px 8px; background: var(--neon-gold); border: 1px solid var(--neon-gold);
        color: #000; font-family: 'Orbitron', sans-serif; font-size: 10px;
        font-weight: 900; cursor: pointer; text-transform: uppercase;
    }
    .btn-fill:hover { background: #fff; border-color: #fff; }

    .product-detail-panel {
        background: var(--panel-bg); border: 1px solid var(--neon-gold); padding: 24px;
        clip-path: polygon(18px 0, 100% 0, 100% calc(100% - 18px), calc(100% - 18px) 100%, 0 100%, 0 18px);
        display: grid; grid-template-columns: 1.4fr 1fr; gap: 28px; align-items: start;
    }
    @media (max-width: 860px) { .product-detail-panel { grid-template-columns: 1fr; padding: 18px; } }
    .detail-meta { display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0; }
    .meta-box { background: rgba(0, 243, 255, 0.06); border-left: 3px solid var(--neon-cyan); padding: 8px 12px; font-size: 14px; flex: 1 1 140px; }
    .meta-box span { display: block; font-family: 'Orbitron', sans-serif; font-size: 9px; color: var(--neon-cyan); }
    .guide-grid { display: grid; grid-template-columns: 1fr; gap: 10px; margin: 16px 0 20px; }
    .guide-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 183, 0, 0.3); padding: 11px 14px; }
    .guide-item h4 { font-family: 'Orbitron', sans-serif; font-size: 10px; color: var(--neon-cyan); margin-bottom: 4px; letter-spacing: 1px; }
    .guide-item p { font-size: 15px; color: #e2e2f0; line-height: 1.45; }
    .stat-row { margin-bottom: 16px; }
    .stat-header { display: flex; justify-content: space-between; font-family: 'Orbitron', sans-serif; font-size: 11px; margin-bottom: 6px; color: #fff; }
    .stat-bar-bg { width: 100%; height: 9px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 183, 0, 0.4); overflow: hidden; }
    .stat-bar-fill { height: 100%; background: linear-gradient(90deg, var(--neon-cyan), var(--neon-gold)); }

    .panel-box {
        background: var(--panel-bg); border: 1px solid var(--neon-cyan); padding: 22px;
        clip-path: polygon(16px 0, 100% 0, 100% calc(100% - 16px), calc(100% - 16px) 100%, 0 100%, 0 16px);
        box-shadow: 0 0 24px rgba(0, 243, 255, 0.1); margin-bottom: 24px;
    }
    .two-col { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
    label { display: block; font-family: 'Orbitron', sans-serif; font-size: 11px; color: var(--neon-cyan); margin-bottom: 6px; letter-spacing: 1px; }
    input, select {
        width: 100%; padding: 12px; background: rgba(5, 5, 10, 0.95);
        border: 1px solid rgba(255, 183, 0, 0.45); color: #fff;
        font-family: 'Rajdhani', sans-serif; font-size: 17px; font-weight: 600;
        outline: none; margin-bottom: 12px;
    }
    input:focus, select:focus { border-color: var(--neon-cyan); }
    .total-display {
        margin: 12px 0 18px; padding: 14px 18px; background: rgba(255, 183, 0, 0.08);
        border-left: 4px solid var(--neon-gold); display: flex; flex-wrap: wrap;
        justify-content: space-between; align-items: center; gap: 10px; font-family: 'Orbitron', sans-serif;
    }
    .total-display span:last-child { font-size: 24px; color: var(--neon-gold); font-weight: 900; }
    .cyber-btn {
        position: relative; width: 100%; padding: 15px 20px;
        background: linear-gradient(45deg, var(--neon-amber), var(--neon-gold));
        color: #050508; font-family: 'Orbitron', sans-serif; font-size: 13px;
        font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase;
        border: none; cursor: pointer;
        clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px);
    }
    .btn-sm {
        padding: 6px 10px; background: transparent; border: 1px solid var(--neon-gold);
        color: var(--neon-gold); font-family: 'Orbitron', sans-serif; font-size: 9px;
        cursor: pointer; text-transform: uppercase; text-decoration: none; display: inline-block;
    }
    .btn-sm:hover { background: var(--neon-gold); color: #000; }
    .alert-ok {
        background: rgba(0, 243, 255, 0.14); border: 1px solid var(--neon-cyan);
        color: var(--neon-cyan); padding: 14px; margin-bottom: 18px; text-align: center;
        font-family: 'Orbitron', sans-serif; font-size: 12px;
    }
    .alert-err {
        background: rgba(255, 50, 80, 0.16); border: 1px solid #ff3250;
        color: #ff8a9b; padding: 14px; margin-bottom: 18px; text-align: center;
        font-family: 'Orbitron', sans-serif; font-size: 12px;
    }
    .user-badge {
        display: flex; flex-wrap: wrap; align-items: center; gap: 10px; padding: 10px 14px;
        background: rgba(0, 243, 255, 0.08); border: 1px solid var(--neon-cyan);
        font-family: 'Orbitron', sans-serif; font-size: 11px; color: var(--neon-cyan);
        margin-bottom: 18px;
    }
    .badge-paid { color: #00ff9d; border: 1px solid #00ff9d; padding: 2px 7px; font-family: 'Orbitron', sans-serif; font-size: 10px; white-space: nowrap; }
    .badge-unpaid { color: #ff6a00; border: 1px solid #ff6a00; padding: 2px 7px; font-family: 'Orbitron', sans-serif; font-size: 10px; white-space: nowrap; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th { font-family: 'Orbitron', sans-serif; font-size: 10px; color: var(--neon-gold); border-bottom: 2px solid var(--neon-gold); padding: 10px 8px; text-align: left; white-space: nowrap; }
    td { padding: 10px 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 15px; }
    .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .online-hero {
        display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;
        background: rgba(0, 243, 255, 0.06); border: 1px solid var(--neon-cyan);
        padding: 20px; margin-bottom: 22px;
    }
    .online-counter {
        font-family: 'Orbitron', sans-serif; font-size: clamp(32px, 8vw, 52px); font-weight: 900;
        color: var(--neon-gold); text-shadow: 0 0 18px rgba(255, 183, 0, 0.6);
    }
    .pulse-dot {
        display: inline-block; width: 10px; height: 10px; border-radius: 50%;
        background: #00ff9d; box-shadow: 0 0 10px #00ff9d; margin-right: 8px;
        animation: pulseOnline 1.2s infinite;
    }
    @keyframes pulseOnline { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.5; } }

    @media (max-width: 600px) {
        #cursor-glow { width: 240px; height: 240px; }
        .sub-tabs { grid-template-columns: repeat(2, 1fr); }
        .nav-bar .nav-link { flex: 1 1 auto; text-align: center; padding: 9px 10px; font-size: 9px; }
        .panel-box { padding: 16px; }
    }
</style>
"""

header_html = """
<div id="cursor-glow"></div>
<div class="hex-bg"></div>

<header>
    <a class="brand-box" href="/">
        <svg class="bee-logo-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="50,3 93,27 93,73 50,97 7,73 7,27" stroke="#ffb700" stroke-width="2.5" fill="rgba(255,183,0,0.06)"/>
            <path class="logo-wing" d="M44 42 L14 22 L10 42 L38 50 Z" fill="rgba(0,243,255,0.25)" stroke="#00f3ff" stroke-width="2"/>
            <path class="logo-wing" d="M56 42 L86 22 L90 42 L62 50 Z" fill="rgba(0,243,255,0.25)" stroke="#00f3ff" stroke-width="2"/>
            <polygon points="50,36 62,48 58,76 50,86 42,76 38,48" fill="#ffb700"/>
            <line x1="40" y1="54" x2="60" y2="54" stroke="#06060a" stroke-width="3.5"/>
            <line x1="41" y1="64" x2="59" y2="64" stroke="#06060a" stroke-width="3.5"/>
            <line x1="44" y1="73" x2="56" y2="73" stroke="#06060a" stroke-width="3"/>
            <polygon points="50,20 60,28 57,37 43,37 40,28" fill="#11111a" stroke="#00f3ff" stroke-width="2"/>
            <line x1="43" y1="29" x2="57" y2="29" stroke="#00f3ff" stroke-width="3"/>
            <polyline points="45,21 38,11 31,11" stroke="#ffb700" stroke-width="2" fill="none"/>
            <polyline points="55,21 62,11 69,11" stroke="#ffb700" stroke-width="2" fill="none"/>
        </svg>
        <div class="brand-text">
            <span class="sys-tag">ALPINE BIO-NETWORK // V.2077</span>
            <h1>CYBER<span>BEE</span></h1>
        </div>
    </a>

    <nav class="nav-bar">
        <a class="nav-link {% if active_page == 'home' %}active-page{% endif %}" href="/">01 // МАГАЗИН</a>
        <a class="nav-link {% if active_page == 'auth' %}active-page{% endif %}" href="/auth">02 // АККАУНТ</a>
        <a class="nav-link {% if active_page == 'online' %}active-page{% endif %}" href="/online">03 // ОНЛАЙН</a>
    </nav>
</header>
"""

interactive_bg_script = """
<script>
    const glow = document.getElementById('cursor-glow');
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    function updatePointer(x, y) {
        mouseX = x;
        mouseY = y;
        if (glow) {
            glow.style.left = mouseX + 'px';
            glow.style.top = mouseY + 'px';
        }
    }

    window.addEventListener('mousemove', (e) => updatePointer(e.clientX, e.clientY));
    window.addEventListener('touchmove', (e) => {
        if (e.touches && e.touches[0]) {
            updatePointer(e.touches[0].clientX, e.touches[0].clientY);
        }
    }, { passive: true });

    const bees = [];
    const BEE_COUNT = window.innerWidth < 600 ? 4 : 7;

    for (let i = 0; i < BEE_COUNT; i++) {
        const el = document.createElement('div');
        el.className = 'smart-bee';
        document.body.appendChild(el);
        bees.push({
            el: el,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * 2.0,
            vy: (Math.random() - 0.5) * 2.0,
            mode: i % 2 === 0 ? 'attract' : 'evade'
        });
    }

    function animateBees() {
        for (const b of bees) {
            const dx = mouseX - b.x;
            const dy = mouseY - b.y;
            const dist = Math.hypot(dx, dy);

            if (dist < 200 && dist > 1) {
                const force = (200 - dist) / 200 * 0.32;
                if (b.mode === 'attract') {
                    b.vx += (dx / dist) * force - (dy / dist) * 0.16;
                    b.vy += (dy / dist) * force + (dx / dist) * 0.16;
                } else {
                    b.vx -= (dx / dist) * force * 1.3;
                    b.vy -= (dy / dist) * force * 1.3;
                }
            } else {
                b.vx += (Math.random() - 0.5) * 0.12;
                b.vy += (Math.random() - 0.5) * 0.12;
            }

            const speed = Math.hypot(b.vx, b.vy);
            if (speed > 3.8) {
                b.vx = (b.vx / speed) * 3.8;
                b.vy = (b.vy / speed) * 3.8;
            }

            b.x += b.vx;
            b.y += b.vy;

            const maxX = Math.max(20, window.innerWidth - 22);
            const maxY = Math.max(20, window.innerHeight - 22);
            if (b.x < 8) { b.x = 8; b.vx *= -1; }
            if (b.x > maxX) { b.x = maxX; b.vx *= -1; }
            if (b.y < 8) { b.y = 8; b.vy *= -1; }
            if (b.y > maxY) { b.y = maxY; b.vy *= -1; }

            const angle = Math.atan2(b.vy, b.vx) * (180 / Math.PI);
            b.el.style.transform = `translate(${b.x}px, ${b.y}px) rotate(${angle}deg)`;
        }
        requestAnimationFrame(animateBees);
    }
    animateBees();
</script>
"""

main_page_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBERBEE // Магазин</title>
    """ + base_style + """
</head>
<body>
""" + header_html + """
<div class="container">
    {% if msg_ok %}<div class="alert-ok">{{ msg_ok }}</div>{% endif %}
    {% if msg_err %}<div class="alert-err">{{ msg_err }}</div>{% endif %}

    {% if current_user %}
    <div class="user-badge">
        <span>АКТИВНЫЙ КЛИЕНТ: {{ current_user }}</span>
        <a class="btn-sm" href="/logout">ВЫЙТИ</a>
    </div>
    {% endif %}

    <div class="sub-tabs">
        <button class="tab-btn active" id="btn-home" onclick="openTab('tab-home', this)">КАТАЛОГ (6)</button>
        {% for t in tovary %}
        <button class="tab-btn" id="btn-{{ t.id }}" onclick="openTab('tab-{{ t.id }}', this)">{{ t.nazvanie }}</button>
        {% endfor %}
        <button class="tab-btn" id="btn-order" onclick="openTab('tab-order', this)">ЗАКАЗ</button>
    </div>

    <div id="tab-home" class="tab-content active">
        <div class="section-title">БИО-МОДУЛИ ПАСЕК CYBERBEE</div>
        <div class="katalog">
            {% for t in tovary %}
            <div class="kartochka">
                <div>
                    <div class="card-top">
                        <div class="honey-logo-wrap">{{ t.svg_logo | safe }}</div>
                        <div>
                            <div class="item-code">{{ t.kod }}</div>
                            <div class="paseka-tag">{{ t.paseka }}</div>
                        </div>
                    </div>
                    <h3>{{ t.nazvanie }}</h3>
                    <p>{{ t.kratko }}</p>

                    <div class="bju-mini">
                        <div><span>БЕЛКИ</span><strong>{{ t.bju.b }}</strong></div>
                        <div><span>ЖИРЫ</span><strong>{{ t.bju.j }}</strong></div>
                        <div><span>УГЛЕВОДЫ</span><strong>{{ t.bju.u }}</strong></div>
                        <div><span>ККАЛ</span><strong>{{ t.bju.kcal }}</strong></div>
                    </div>

                    <div class="info-snippet">
                        <strong>С ЧЕМ КУШАТЬ:</strong>
                        {{ t.s_chem }}
                    </div>
                </div>
                <div>
                    <div class="card-footer">
                        <span class="ves-badge">ОБЪЁМ: {{ t.ves }}</span>
                        <div class="cena">{{ t.cena }} ₽</div>
                    </div>
                    <div class="card-actions">
                        <button type="button" class="btn-outline" onclick="openTab('tab-{{ t.id }}', document.getElementById('btn-{{ t.id }}'))">Состав и приём</button>
                        <button type="button" class="btn-fill" onclick="zakazatSrazu('{{ t.nazvanie }}')">Заказать</button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    {% for t in tovary %}
    <div id="tab-{{ t.id }}" class="tab-content">
        <div class="section-title">СПЕЦИФИКАЦИЯ // {{ t.kod }}</div>
        <div class="product-detail-panel">
            <div>
                <div style="display:flex; align-items:center; gap:14px; margin-bottom:14px;">
                    {{ t.svg_logo | safe }}
                    <div>
                        <div class="item-code">{{ t.paseka }}</div>
                        <h2 style="font-family: 'Orbitron', sans-serif; font-size: clamp(20px, 5vw, 28px); color: #fff;">{{ t.nazvanie }}</h2>
                    </div>
                </div>

                <p style="font-size: 16px; line-height: 1.55; color: #c8c8dc;">{{ t.polnoe }}</p>

                <div class="detail-meta">
                    <div class="meta-box"><span>МАССА НЕТТО</span><strong>{{ t.ves }}</strong></div>
                    <div class="meta-box"><span>Б / Ж / У</span><strong>{{ t.bju.b }} / {{ t.bju.j }} / {{ t.bju.u }}</strong></div>
                    <div class="meta-box"><span>КАЛОРИЙНОСТЬ</span><strong>{{ t.bju.kcal }} / 100 г</strong></div>
                    <div class="meta-box"><span>СТОИМОСТЬ</span><strong style="color: var(--neon-gold);">{{ t.cena }} ₽</strong></div>
                </div>

                <div class="guide-grid">
                    <div class="guide-item">
                        <h4>ПОЛЕЗНЫЕ СВОЙСТВА</h4>
                        <p>{{ t.svoystva }}</p>
                    </div>
                    <div class="guide-item">
                        <h4>УСЛОВИЯ ПРИЁМА</h4>
                        <p>{{ t.usloviya }}</p>
                    </div>
                    <div class="guide-item">
                        <h4>С ЧЕМ ЛУЧШЕ УПОТРЕБЛЯТЬ</h4>
                        <p>{{ t.s_chem }}</p>
                    </div>
                </div>

                <button type="button" class="cyber-btn" onclick="zakazatSrazu('{{ t.nazvanie }}')">ОФОРМИТЬ ЗАКАЗ — {{ t.cena }} ₽</button>
            </div>
            <div style="background: rgba(5,5,10,0.75); padding: 20px; border: 1px solid rgba(0,243,255,0.3);">
                <div class="item-code" style="margin-bottom: 16px;">БИО-МЕТРИКИ СОРТА</div>
                {% for stat_name, stat_val in t.stats.items() %}
                <div class="stat-row">
                    <div class="stat-header"><span>{{ stat_name }}</span><span style="color: var(--neon-gold);">{{ stat_val }}%</span></div>
                    <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ stat_val }}%;"></div></div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endfor %}

    <div id="tab-order" class="tab-content">
        <div class="panel-box">
            <div class="section-title">ТЕРМИНАЛ ОФОРМЛЕНИЯ ЗАКАЗА</div>
            {% if not current_user %}
            <div class="alert-err">
                Для оформления заказа войдите или зарегистрируйтесь по почте / телефону и паролю во вкладке <a href="/auth" style="color:#fff;">02 // АККАУНТ</a>.
            </div>
            {% endif %}
            <form method="POST" action="/zakaz">
                <div class="form-grid">
                    <div>
                        <label>ИМЯ ПОЛУЧАТЕЛЯ</label>
                        <input type="text" name="imya" required placeholder="Введите имя...">
                    </div>
                    <div>
                        <label>ТЕЛЕФОН ДЛЯ СВЯЗИ</label>
                        <input type="text" name="telefon" required placeholder="+7 (999) 000-00-00">
                    </div>
                    <div>
                        <label>СОРТ МЁДА</label>
                        <select name="tovar" id="select-tovar" onchange="pereschitat()">
                            {% for t in tovary %}
                            <option value="{{ t.nazvanie }}" data-price="{{ t.cena }}">{{ t.nazvanie }} — {{ t.cena }} ₽</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label>КОЛИЧЕСТВО БАНОК</label>
                        <input type="number" name="kolvo" id="input-kolvo" value="1" min="1" max="50" required oninput="pereschitat()">
                    </div>
                </div>

                <label style="display:flex; align-items:center; gap:10px; cursor:pointer; color:#e0e0e0; margin-top:4px;">
                    <input type="checkbox" name="pay_now" value="1" style="width:auto; margin:0;">
                    Оплатить заказ сразу (отметить как оплаченный)
                </label>

                <div class="total-display">
                    <span>ИТОГО К ОПЛАТЕ:</span>
                    <span id="itogo-cena">1500 ₽</span>
                </div>
                <button type="submit" class="cyber-btn">ПОДТВЕРДИТЬ ЗАКАЗ</button>
            </form>
        </div>

        {% if user_orders %}
        <div class="panel-box">
            <div class="section-title" style="font-size:15px;">МОИ ЗАКАЗЫ</div>
            <div class="table-wrap">
                <table>
                    <tr>
                        <th>ID</th>
                        <th>МОДУЛЬ</th>
                        <th>КОЛ-ВО</th>
                        <th>СУММА</th>
                        <th>СТАТУС</th>
                        <th>ДЕЙСТВИЕ</th>
                    </tr>
                    {% for o in user_orders %}
                    <tr>
                        <td style="color:var(--neon-cyan);">#{{ o['id'] }}</td>
                        <td>{{ o['tovar'] }}</td>
                        <td>{{ o['kolvo'] }} шт.</td>
                        <td style="color:var(--neon-gold); font-weight:bold;">{{ o['summa'] }} ₽</td>
                        <td>
                            {% if o['paid'] %}
                            <span class="badge-paid">ОПЛАЧЕН</span>
                            {% else %}
                            <span class="badge-unpaid">НЕ ОПЛАЧЕН</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if not o['paid'] %}
                            <a class="btn-sm" href="/pay_order/{{ o['id'] }}">ОПЛАТИТЬ</a>
                            {% else %}
                            —
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        {% endif %}
    </div>
</div>

<script>
    function openTab(tabId, btnElement) {
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        if (btnElement) btnElement.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    function pereschitat() {
        const select = document.getElementById('select-tovar');
        const cena = select.options[select.selectedIndex].getAttribute('data-price');
        const kolvo = document.getElementById('input-kolvo').value || 1;
        document.getElementById('itogo-cena').innerText = (cena * kolvo) + ' ₽';
    }
    function zakazatSrazu(nazvanie) {
        const select = document.getElementById('select-tovar');
        select.value = nazvanie;
        pereschitat();
        openTab('tab-order', document.getElementById('btn-order'));
    }
    {% if open_order %}
    openTab('tab-order', document.getElementById('btn-order'));
    {% endif %}
</script>
""" + interactive_bg_script + """
</body>
</html>
"""

auth_page_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBERBEE // Аккаунт и вход</title>
    """ + base_style + """
</head>
<body>
""" + header_html + """
<div class="container">
    {% if msg_ok %}<div class="alert-ok">{{ msg_ok }}</div>{% endif %}
    {% if msg_err %}<div class="alert-err">{{ msg_err }}</div>{% endif %}

    {% if is_admin %}
    <div class="user-badge">
        <span>АКТИВНА СЕССИЯ АДМИНИСТРАТОРА: {{ admin_login }}</span>
        <a class="btn-sm" href="/admin">ОТКРЫТЬ АДМИН-ПАНЕЛЬ</a>
        <a class="btn-sm" href="/admin/logout">ВЫЙТИ</a>
    </div>
    {% endif %}

    {% if current_user %}
    <div class="user-badge">
        <span>ВЫ ВОШЛИ КАК: {{ current_user }}</span>
        <a class="btn-sm" href="/logout">ВЫЙТИ</a>
    </div>
    {% endif %}

    <div class="two-col">
        <div class="panel-box">
            <div class="section-title">РЕГИСТРАЦИЯ КЛИЕНТА</div>
            <form method="POST" action="/register">
                <label>ПОЧТА ИЛИ НОМЕР ТЕЛЕФОНА</label>
                <input type="text" name="contact" required placeholder="user@mail.ru или +79990001122">

                <label>ПАРОЛЬ</label>
                <input type="password" name="password" required placeholder="Придумайте пароль">

                <button type="submit" class="cyber-btn">ЗАРЕГИСТРИРОВАТЬСЯ</button>
            </form>
        </div>

        <div class="panel-box">
            <div class="section-title">ВХОД В СИСТЕМУ</div>
            <form method="POST" action="/login">
                <label>ПОЧТА / ТЕЛЕФОН ИЛИ ЛОГИН</label>
                <input type="text" name="contact" required placeholder="Почта, телефон или логин доступа">

                <label>ПАРОЛЬ</label>
                <input type="password" name="password" required placeholder="Введите пароль">

                <button type="submit" class="cyber-btn">ВОЙТИ В АККАУНТ</button>
            </form>
        </div>
    </div>
</div>
""" + interactive_bg_script + """
</body>
</html>
"""

online_page_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBERBEE // Онлайн и активные заказчики</title>
    """ + base_style + """
</head>
<body>
""" + header_html + """
<div class="container">
    <div class="panel-box">
        <div class="section-title">МОНИТОРИНГ АКТИВНОСТИ СЕТИ CYBERBEE</div>
        <div class="online-hero">
            <div>
                <div class="item-code"><span class="pulse-dot"></span>ТЕКУЩИЙ ОНЛАЙН В СЕТИ (234 — 516)</div>
                <div style="font-size:15px; color:#b8b8cc; margin-top:6px;">
                    Обновление телеметрии каждые 1–10 сек. Шаг изменения: до ±10 человек.
                </div>
            </div>
            <div style="text-align:right;">
                <div class="online-counter"><span id="online-num">348</span> <span style="font-size:16px; color:var(--neon-cyan);">ЧЕЛ.</span></div>
                <div id="online-delta" style="font-family:'Orbitron',sans-serif; font-size:11px; color:#00ff9d;">СТАБИЛЬНЫЙ ПОТОК</div>
            </div>
        </div>

        <div class="section-title" style="font-size:16px;">АКТИВНЫЕ ЗАКАЗЧИКИ</div>
        <div class="table-wrap">
            <table>
                <tr>
                    <th>ЗАКАЗЧИК</th>
                    <th>СОРТ МЁДА</th>
                    <th>ОБЪЁМ</th>
                    <th>СТАТУС</th>
                </tr>
                <tbody id="live-customers-body">
                    {% for z in recent_orders %}
                    <tr>
                        <td style="color:var(--neon-cyan);">{{ z['imya'] }}</td>
                        <td>{{ z['tovar'] }}</td>
                        <td>{{ z['kolvo'] }} шт.</td>
                        <td>
                            {% if z['paid'] %}
                            <span class="badge-paid">ОПЛАЧЕН</span>
                            {% else %}
                            <span class="badge-unpaid">ОФОРМЛЯЕТСЯ</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    let currentOnline = Math.floor(Math.random() * (516 - 234 + 1)) + 234;
    const onlineEl = document.getElementById('online-num');
    const deltaEl = document.getElementById('online-delta');
    onlineEl.innerText = currentOnline;

    const sampleNames = ['Алексей К.', 'Марина В.', 'Дмитрий С.', 'Елена Р.', 'Артём Н.', 'Кирилл Т.', 'София Л.', 'Максим Г.', 'Виктория О.', 'Денис П.'];
    const sampleHoneys = [
        'АЛЬПИЙСКИЙ СИНТЕЗ',
        'НЕКТАР БЕЛОКУРЫХ ПЧЁЛ',
        'КИБЕР-ПРОПОЛИС GOLD',
        'КЕДРОВО-ХВОЙНЫЙ НЕКТАР',
        'ДИКИЙ ГОРНЫЙ КАШТАН',
        'МАТОЧНЫЙ ЭЛИКСИР БЕЛОКУРЫХ'
    ];

    function updateOnlineTick() {
        let step = 0;
        while (step === 0) {
            step = Math.floor(Math.random() * 21) - 10;
        }

        let nextOnline = currentOnline + step;
        if (nextOnline > 516) nextOnline = 516 - Math.floor(Math.random() * 6);
        if (nextOnline < 234) nextOnline = 234 + Math.floor(Math.random() * 6);

        const realDiff = nextOnline - currentOnline;
        currentOnline = nextOnline;
        onlineEl.innerText = currentOnline;

        if (realDiff > 0) {
            deltaEl.style.color = '#00ff9d';
            deltaEl.innerText = `+${realDiff} ПОДКЛЮЧИЛИСЬ`;
        } else {
            deltaEl.style.color = '#ff6a00';
            deltaEl.innerText = `${realDiff} ОТКЛЮЧИЛИСЬ`;
        }

        if (Math.random() > 0.45) {
            const tbody = document.getElementById('live-customers-body');
            const tr = document.createElement('tr');
            const name = sampleNames[Math.floor(Math.random() * sampleNames.length)];
            const honey = sampleHoneys[Math.floor(Math.random() * sampleHoneys.length)];
            const qty = Math.floor(Math.random() * 3) + 1;
            const isPaid = Math.random() > 0.35;

            tr.innerHTML = `
                <td style="color:var(--neon-cyan);">${name}</td>
                <td>${honey}</td>
                <td>${qty} шт.</td>
                <td>${isPaid ? '<span class="badge-paid">ОПЛАЧЕН</span>' : '<span class="badge-unpaid">ОФОРМЛЯЕТСЯ</span>'}</td>
            `;
            tbody.insertBefore(tr, tbody.firstChild);
            if (tbody.children.length > 12) {
                tbody.removeChild(tbody.lastChild);
            }
        }

        const nextDelayMs = (Math.floor(Math.random() * 10) + 1) * 1000;
        setTimeout(updateOnlineTick, nextDelayMs);
    }

    setTimeout(updateOnlineTick, (Math.floor(Math.random() * 10) + 1) * 1000);
</script>
""" + interactive_bg_script + """
</body>
</html>
"""

admin_panel_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBERBEE // Админ-панель, оплаченные заказы и логи</title>
    """ + base_style + """
</head>
<body>
""" + header_html + """
<div class="container">
    <div class="user-badge">
        <span>АДМИНИСТРАТОР: {{ admin_login }}</span>
        <a class="btn-sm" href="/admin/logout">ВЫЙТИ ИЗ АДМИНКИ</a>
    </div>

    {% if msg_ok %}<div class="alert-ok">{{ msg_ok }}</div>{% endif %}

    <div class="panel-box">
        <div class="section-title">ОПЛАЧЕННЫЕ ЗАКАЗЫ</div>
        <div class="table-wrap">
            <table>
                <tr>
                    <th>ID</th>
                    <th>АККАУНТ</th>
                    <th>ИМЯ</th>
                    <th>ТЕЛЕФОН</th>
                    <th>МОДУЛЬ</th>
                    <th>КОЛ-ВО</th>
                    <th>СУММА</th>
                    <th>СТАТУС</th>
                </tr>
                {% for z in paid_orders %}
                <tr>
                    <td style="color:var(--neon-cyan);">#{{ z['id'] }}</td>
                    <td>{{ z['user_contact'] or '—' }}</td>
                    <td>{{ z['imya'] }}</td>
                    <td>{{ z['telefon'] }}</td>
                    <td>{{ z['tovar'] }}</td>
                    <td>{{ z['kolvo'] }} шт.</td>
                    <td style="color:var(--neon-gold); font-weight:bold;">{{ z['summa'] }} ₽</td>
                    <td><span class="badge-paid">ОПЛАЧЕН</span></td>
                </tr>
                {% endfor %}
                {% if not paid_orders %}
                <tr><td colspan="8" style="color:#888;">Оплаченных заказов пока нет.</td></tr>
                {% endif %}
            </table>
        </div>
    </div>

    <div class="panel-box">
        <div class="section-title">ВСЕ ЗАКАЗЫ (УПРАВЛЕНИЕ ОПЛАТОЙ)</div>
        <div class="table-wrap">
            <table>
                <tr>
                    <th>ID</th>
                    <th>АККАУНТ</th>
                    <th>ИМЯ</th>
                    <th>ТЕЛЕФОН</th>
                    <th>МОДУЛЬ</th>
                    <th>КОЛ-ВО</th>
                    <th>СУММА</th>
                    <th>СТАТУС</th>
                    <th>ДЕЙСТВИЕ</th>
                </tr>
                {% for z in all_orders %}
                <tr>
                    <td style="color:var(--neon-cyan);">#{{ z['id'] }}</td>
                    <td>{{ z['user_contact'] or '—' }}</td>
                    <td>{{ z['imya'] }}</td>
                    <td>{{ z['telefon'] }}</td>
                    <td>{{ z['tovar'] }}</td>
                    <td>{{ z['kolvo'] }} шт.</td>
                    <td style="color:var(--neon-gold); font-weight:bold;">{{ z['summa'] }} ₽</td>
                    <td>
                        {% if z['paid'] %}
                        <span class="badge-paid">ОПЛАЧЕН</span>
                        {% else %}
                        <span class="badge-unpaid">НЕ ОПЛАЧЕН</span>
                        {% endif %}
                    </td>
                    <td>
                        <a class="btn-sm" href="/admin/toggle_paid/{{ z['id'] }}">
                            {% if z['paid'] %}СНЯТЬ ОПЛАТУ{% else %}ОТМЕТИТЬ ОПЛАЧЕННЫМ{% endif %}
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <div class="panel-box">
        <div class="section-title">СИСТЕМНЫЕ ЛОГИ CYBERBEE</div>
        <div class="table-wrap">
            <table>
                <tr>
                    <th>ID</th>
                    <th>ВРЕМЯ</th>
                    <th>СУБЪЕКТ</th>
                    <th>СОБЫТИЕ</th>
                </tr>
                {% for l in logs %}
                <tr>
                    <td style="color:var(--neon-cyan);">#{{ l['id'] }}</td>
                    <td>{{ l['created_at'] }}</td>
                    <td style="color:var(--neon-gold);">{{ l['actor'] }}</td>
                    <td>{{ l['action'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</div>
""" + interactive_bg_script + """
</body>
</html>
"""


@app.route("/")
def index():
    msg_ok = session.pop("msg_ok", None)
    msg_err = session.pop("msg_err", None)
    open_order = session.pop("open_order", False)
    user_contact = session.get("user_contact")
    user_id = session.get("user_id")

    user_orders = []
    if user_id:
        conn = get_db()
        user_orders = conn.execute(
            "SELECT * FROM zakazy WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
        conn.close()

    return render_template_string(
        main_page_html,
        active_page="home",
        tovary=tovary,
        current_user=user_contact,
        user_orders=user_orders,
        msg_ok=msg_ok,
        msg_err=msg_err,
        open_order=open_order,
    )


@app.route("/online")
def online_page():
    conn = get_db()
    recent_orders = conn.execute(
        "SELECT imya, tovar, kolvo, paid FROM zakazy ORDER BY id DESC LIMIT 8"
    ).fetchall()
    conn.close()
    return render_template_string(
        online_page_html,
        active_page="online",
        recent_orders=recent_orders,
    )


@app.route("/auth")
def auth_page():
    msg_ok = session.pop("msg_ok", None)
    msg_err = session.pop("msg_err", None)
    return render_template_string(
        auth_page_html,
        active_page="auth",
        current_user=session.get("user_contact"),
        is_admin=session.get("is_admin"),
        admin_login=ADMIN_LOGIN,
        msg_ok=msg_ok,
        msg_err=msg_err,
    )


@app.route("/register", methods=["POST"])
def register():
    contact = request.form["contact"].strip()
    password = request.form["password"].strip()

    if not contact or not password or contact == ADMIN_LOGIN:
        session["msg_err"] = "Укажите корректную почту/телефон и пароль."
        return redirect("/auth")

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE contact = ?", (contact,)).fetchone()
    if existing:
        conn.close()
        session["msg_err"] = "Этот контакт уже зарегистрирован."
        return redirect("/auth")

    cur = conn.cursor()
    cur.execute("INSERT INTO users (contact, password) VALUES (?, ?)", (contact, password))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    session["user_id"] = user_id
    session["user_contact"] = contact
    write_log(contact, "Регистрация нового клиента")
    session["msg_ok"] = f"Аккаунт {contact} создан. Вход выполнен."
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    contact = request.form["contact"].strip()
    password = request.form["password"].strip()

    if contact == ADMIN_LOGIN and password == ADMIN_PASS:
        session["is_admin"] = True
        write_log(ADMIN_LOGIN, "Вход в админ-панель через окно авторизации")
        return redirect("/admin")

    conn = get_db()
    user = conn.execute(
        "SELECT id, contact FROM users WHERE contact = ? AND password = ?", (contact, password)
    ).fetchone()
    conn.close()

    if not user:
        write_log(contact or "unknown", "Неудачная попытка входа")
        session["msg_err"] = "Неверный логин/контакт или пароль."
        return redirect("/auth")

    session["user_id"] = user["id"]
    session["user_contact"] = user["contact"]
    write_log(user["contact"], "Вход клиента в аккаунт")
    session["msg_ok"] = f"Добро пожаловать, {user['contact']}."
    return redirect("/")


@app.route("/logout")
def logout():
    actor = session.get("user_contact") or "гость"
    session.pop("user_id", None)
    session.pop("user_contact", None)
    write_log(actor, "Выход клиента из аккаунта")
    return redirect("/")


@app.route("/zakaz", methods=["POST"])
def sdelat_zakaz():
    if not session.get("user_id"):
        session["msg_err"] = "Сначала войдите или зарегистрируйтесь по почте / телефону и паролю во вкладке Аккаунт."
        session["open_order"] = True
        return redirect("/")

    imya = request.form["imya"].strip()
    telefon = request.form["telefon"].strip()
    vybranny_tovar = request.form["tovar"]
    kolvo = int(request.form["kolvo"])
    paid = 1 if request.form.get("pay_now") == "1" else 0

    cena = 0
    for t in tovary:
        if t["nazvanie"] == vybranny_tovar:
            cena = t["cena"]
            break

    itogo = cena * kolvo

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO zakazy (user_id, imya, telefon, tovar, kolvo, summa, paid)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session["user_id"], imya, telefon, vybranny_tovar, kolvo, itogo, paid),
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    status_txt = "оплачен" if paid else "ожидает оплаты"
    write_log(session["user_contact"], f"Создан заказ #{order_id} ({vybranny_tovar}, {kolvo} шт., {itogo} ₽, {status_txt})")
    session["msg_ok"] = f"Заказ #{order_id} оформлен ({status_txt})."
    session["open_order"] = True
    return redirect("/")


@app.route("/pay_order/<int:order_id>")
def pay_order(order_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/auth")

    conn = get_db()
    order = conn.execute("SELECT * FROM zakazy WHERE id = ? AND user_id = ?", (order_id, user_id)).fetchone()
    if order:
        conn.execute("UPDATE zakazy SET paid = 1 WHERE id = ?", (order_id,))
        conn.commit()
        write_log(session.get("user_contact"), f"Оплатил заказ #{order_id} на сумму {order['summa']} ₽")
        session["msg_ok"] = f"Заказ #{order_id} отмечен как оплаченный."
    conn.close()
    session["open_order"] = True
    return redirect("/")


@app.route("/admin")
@admin_required
def admin_page():
    msg_ok = session.pop("msg_ok", None)
    conn = get_db()
    paid_orders = conn.execute("""
        SELECT z.*, u.contact AS user_contact
        FROM zakazy z
        LEFT JOIN users u ON z.user_id = u.id
        WHERE z.paid = 1
        ORDER BY z.id DESC
    """).fetchall()

    all_orders = conn.execute("""
        SELECT z.*, u.contact AS user_contact
        FROM zakazy z
        LEFT JOIN users u ON z.user_id = u.id
        ORDER BY z.id DESC
    """).fetchall()

    logs = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()

    return render_template_string(
        admin_panel_html,
        active_page="auth",
        admin_login=ADMIN_LOGIN,
        paid_orders=paid_orders,
        all_orders=all_orders,
        logs=logs,
        msg_ok=msg_ok,
    )


@app.route("/admin/toggle_paid/<int:order_id>")
@admin_required
def admin_toggle_paid(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM zakazy WHERE id = ?", (order_id,)).fetchone()
    if order:
        new_paid = 0 if order["paid"] else 1
        conn.execute("UPDATE zakazy SET paid = ? WHERE id = ?", (new_paid, order_id))
        conn.commit()
        state_str = "ОПЛАЧЕН" if new_paid else "НЕ ОПЛАЧЕН"
        write_log(ADMIN_LOGIN, f"Изменил статус заказа #{order_id} на {state_str}")
        session["msg_ok"] = f"Статус заказа #{order_id} обновлён: {state_str}."
    conn.close()
    return redirect("/admin")


@app.route("/admin/logout")
def admin_logout():
    if session.get("is_admin"):
        write_log(ADMIN_LOGIN, "Выход из админ-панели")
    session.pop("is_admin", None)
    return redirect("/auth")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)