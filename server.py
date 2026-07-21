import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from fastapi import FastAPI
import uvicorn

app = FastAPI()
DB_NAME = "asgard_cloud.db"

# --- НАЛАШТУВАННЯ GMAIL (НЕОБОВ'ЯЗКОВО) ---
GMAIL_USER = ""      # Наприклад: "asgard.bot@gmail.com"
GMAIL_PASSWORD = ""  # Пароль додатка Google (App Password)

def send_gmail_notification(to_email: str, subject: str, text: str):
    if not GMAIL_USER or not GMAIL_PASSWORD or not to_email or "@" not in to_email:
        print(f"[ПОШТА (ІМІТАЦІЯ)] Лист для {to_email}: {subject} -> {text}")
        return
    try:
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = f"Королівство Азгард <{GMAIL_USER}>"
        msg['To'] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[ПОШТА ВІДПРАВЛЕНА] Лист успішно надіслано на {to_email}")
    except Exception as e:
        print(f"Помилка надсилання пошти: {e}")

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                user_id INTEGER UNIQUE,
                role TEXT,
                balance REAL,
                email TEXT DEFAULT '',
                is_banned INTEGER DEFAULT 0,
                vip_level INTEGER DEFAULT 0,
                permit_sell INTEGER DEFAULT 0,
                permit_territory INTEGER DEFAULT 0,
                permit_food INTEGER DEFAULT 0,
                permit_weapons INTEGER DEFAULT 0,
                permit_tools INTEGER DEFAULT 0
            )
        ''')
        
        # Додаємо колонку email, якщо база була створена раніше
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                text TEXT,
                timestamp TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                receiver TEXT,
                text TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter TEXT,
                target TEXT,
                reason TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS royal_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                target TEXT,
                text TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank (
                id INTEGER PRIMARY KEY,
                capital REAL
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM bank")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO bank (id, capital) VALUES (1, 1000000.0)")
            
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller TEXT,
                item_name TEXT,
                price REAL,
                description TEXT
            )
        ''')
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Помилка БД сервера: {e}")

init_db()

def generate_unique_id(cursor):
    while True:
        new_id = random.randint(10, 99)
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (new_id,))
        if cursor.fetchone()[0] == 0:
            return new_id

def resolve_target_internal(cursor, identifier):
    identifier = str(identifier).strip()
    if not identifier:
        return None
    if identifier.isdigit() and len(identifier) == 2:
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (int(identifier),))
        res = cursor.fetchone()
        return res[0] if res else None
    else:
        cursor.execute("SELECT username FROM users WHERE username = ?", (identifier,))
        res = cursor.fetchone()
        return res[0] if res else None

# === ЕНДПОІНТИ СЕРВЕРА ===

@app.post("/login")
def login(data: dict):
    username = data.get("username", "").strip()
    auth_code = data.get("auth_code", "").strip()
    
    if not username:
        return {"status": "error", "message": "Нікнейм порожній!"}
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role, balance, is_banned, user_id, email FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    target_role = None
    if auth_code == "3633_ADMIN":
        target_role = "Адмін"
    elif auth_code.upper() == "3633АЗГАРД":
        target_role = "Король"
        
    if user:
        role, balance, is_banned, user_id, email = user
        if is_banned == 1 and target_role != "Адмін":
            conn.close()
            return {"status": "error", "message": "Ви забанені Королем за порушення законів!"}
            
        if target_role:
            if role != target_role:
                cursor.execute("UPDATE users SET role = ? WHERE username = ?", (target_role, username))
                conn.commit()
                role = target_role
        else:
            if role in ["Король", "Адмін"]:
                conn.close()
                return {"status": "error", "message": "НЕВІРНИЙ КОД ДОСТУПУ ДЛЯ ВЕРХІВКИ!"}
    else:
        role = target_role if target_role else "Громадянин"
        balance = 0.0
        email = ""
        user_id = generate_unique_id(cursor)
        cursor.execute("INSERT INTO users (username, user_id, role, balance, email) VALUES (?, ?, ?, ?, ?)",
                       (username, user_id, role, balance, email))
        conn.commit()
        
    conn.close()
    return {"status": "ok", "username": username, "role": role, "balance": balance, "user_id": user_id, "email": email}

@app.post("/set_email")
def set_email(data: dict):
    username = data.get("username")
    email = data.get("email", "").strip()

    if not username or not email or "@" not in email:
        return {"status": "error", "message": "Введіть коректну електронну пошту!"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))
    conn.commit()
    conn.close()

    send_gmail_notification(email, "Азгард: Пошту прив'язано!", f"Вітаємо, {username}! Ваша пошта успішно прив'язана до акаунту в Азгарді.")
    return {"status": "ok", "message": "Пошту успішно прив'язано!"}

@app.get("/user_info/{username}")
def user_info(username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role, balance, user_id, email FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()
    cursor.execute("SELECT capital FROM bank WHERE id = 1")
    bank_res = cursor.fetchone()
    bank_capital = bank_res[0] if bank_res else 0.0
    conn.close()
    
    if res:
        return {"role": res[0], "balance": res[1], "user_id": res[2], "email": res[3], "bank_capital": bank_capital}
    return {"role": "Громадянин", "balance": 0.0, "user_id": "--", "email": "", "bank_capital": bank_capital}

@app.get("/messages")
def get_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT messages.sender, messages.text, messages.timestamp, users.user_id, users.role
        FROM messages 
        LEFT JOIN users ON messages.sender = users.username 
        ORDER BY messages.id DESC LIMIT 30
    ''')
    messages = cursor.fetchall()
    conn.close()
    
    result = []
    for sender, text, timestamp, sender_id, sender_role in reversed(messages):
        result.append({
            "sender": sender,
            "text": text,
            "timestamp": timestamp,
            "sender_id": sender_id if sender_id else "--",
            "sender_role": sender_role if sender_role else "Громадянин"
        })
    return result

@app.post("/send_message")
def send_message(data: dict):
    sender = data.get("sender")
    text = data.get("text")
    if sender and text:
        now = datetime.now().strftime("%H:%M")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)", (sender, text, now))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    return {"status": "error"}

@app.post("/send_pm")
def send_pm(data: dict):
    sender = data.get("sender")
    target_raw = data.get("target")
    text = data.get("text")

    if not text or not target_raw:
        return {"status": "error", "message": "Заповніть всі поля!"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    receiver = resolve_target_internal(cursor, target_raw)
    if not receiver:
        conn.close()
        return {"status": "error", "message": "Отримувача не знайдено!"}

    now = datetime.now().strftime("%H:%M")
    cursor.execute("INSERT INTO private_messages (sender, receiver, text, timestamp) VALUES (?, ?, ?, ?)",
                   (sender, receiver, text, now))

    # Перевіряємо, чи є в отримувача пошта
    cursor.execute("SELECT email FROM users WHERE username = ?", (receiver,))
    res_email = cursor.fetchone()
    if res_email and res_email[0]:
        send_gmail_notification(res_email[0], "Нове особисте повідомлення в Азгарді!", f"Гравець {sender} надіслав вам ЛС: {text}")

    conn.commit()
    conn.close()
    return {"status": "ok", "receiver": receiver}

@app.get("/pms/{username}")
def get_pms(username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, receiver, text, timestamp 
        FROM private_messages 
        WHERE sender = ? OR receiver = ? 
        ORDER BY id DESC LIMIT 40
    ''', (username, username))
    rows = cursor.fetchall()
    conn.close()

    res = []
    for s, r, t, tm in reversed(rows):
        res.append({"sender": s, "receiver": r, "text": t, "timestamp": tm})
    return res

@app.post("/transfer")
def transfer(data: dict):
    sender = data.get("sender")
    target_raw = data.get("target")
    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return {"status": "error", "message": "Некоректна сума!"}

    if amount <= 0:
        return {"status": "error", "message": "Сума повинна бути більшою за 0 Ю!"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    target = resolve_target_internal(cursor, target_raw)
    if not target:
        conn.close()
        return {"status": "error", "message": "Отримувача не знайдено!"}

    if sender == target:
        conn.close()
        return {"status": "error", "message": "Не можна переказувати кошти самому собі!"}

    cursor.execute("SELECT balance FROM users WHERE username = ?", (sender,))
    res = cursor.fetchone()
    if not res or res[0] < amount:
        conn.close()
        return {"status": "error", "message": "Недостатньо коштів на балансі!"}

    cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, sender))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, target))

    now = datetime.now().strftime("%H:%M")
    sys_msg = f"[БАНК]: {sender} переказав {amount:.1f} Ю гравцеві {target}!"
    cursor.execute("INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)", ("Система", sys_msg, now))

    # Сповіщення на пошту
    cursor.execute("SELECT email FROM users WHERE username = ?", (target,))
    res_email = cursor.fetchone()
    if res_email and res_email[0]:
        send_gmail_notification(res_email[0], "Грошовий переказ в Азгарді!", f"Гравець {sender} переказав вам {amount:.1f} Юнітів!")

    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Успішно переказано {amount:.1f} Ю гравцю {target}!"}

@app.get("/king_order")
def king_order():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT type, target, text FROM royal_orders ORDER BY id DESC LIMIT 1")
    res = cursor.fetchone()
    conn.close()
    if res:
        return {"type": res[0], "target": res[1], "text": res[2]}
    return {"type": "", "target": "", "text": ""}

@app.post("/spin_wheel")
def spin_wheel(data: dict):
    username = data.get("username")
    try:
        bet = float(data.get("bet", 0))
    except (ValueError, TypeError):
        return {"status": "error", "message": "Некоректна сума ставки!"}

    if bet <= 0:
        return {"status": "error", "message": "Ставка має бути більшою за 0 Ю!"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()

    if not res:
        conn.close()
        return {"status": "error", "message": "Користувача не знайдено!"}

    balance = res[0]
    if balance < bet:
        conn.close()
        return {"status": "error", "message": "У вас недостатньо коштів для цієї ставки!"}

    outcomes = [2.0, 0.5, 0.0]
    weights = [10, 20, 70]
    multiplier = random.choices(outcomes, weights=weights)[0]

    payout = bet * multiplier
    new_balance = balance - bet + payout

    cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, username))

    if multiplier == 0.0:
        cursor.execute("UPDATE bank SET capital = capital + ? WHERE id = 1", (bet,))

    conn.commit()
    conn.close()

    if multiplier == 2.0:
        msg = f"🔥 СУПЕР ВИГРАШ 2x! Ви виграли {payout:.1f} Ю!"
    elif multiplier == 0.5:
        msg = f"⚡ ПОВЕРНЕННЯ 0.5x. Ви отримали {payout:.1f} Ю."
    else:
        msg = f"💀 БАНКРУТ! Ви втратили {bet:.1f} Ю."

    return {
        "status": "ok",
        "multiplier": multiplier,
        "payout": payout,
        "new_balance": new_balance,
        "message": msg
    }

@app.post("/buy_vip")
def buy_vip(data: dict):
    username = data.get("username")
    level = data.get("level")
    price = data.get("price")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, vip_level FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()
    if not res:
        conn.close()
        return {"status": "error", "message": "Користувача не знайдено"}
    balance, current_vip = res
    if current_vip >= level:
        conn.close()
        return {"status": "error", "message": "Ви вже володієте цим або вищим ВІП-рангом!"}
    if balance < price:
        conn.close()
        return {"status": "error", "message": f"Недостатньо коштів! Потрібно: {price} Ю"}
        
    cursor.execute("UPDATE users SET balance = balance - ?, vip_level = ? WHERE username = ?", (price, level, username))
    cursor.execute("UPDATE bank SET capital = capital + ? WHERE id = 1", (price,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/buy_permit")
def buy_permit(data: dict):
    username = data.get("username")
    key = data.get("key")
    price = data.get("price")
    column_map = {"sell": "permit_sell", "territory": "permit_territory", "food": "permit_food", "weapons": "permit_weapons", "tools": "permit_tools"}
    col = column_map.get(key)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT balance, {col} FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()
    if not res:
        conn.close()
        return {"status": "error", "message": "Користувача не знайдено"}
    balance, has_permit = res
    if has_permit == 1:
        conn.close()
        return {"status": "error", "message": "Ви вже маєте цей дозвіл!"}
    if balance < price:
        conn.close()
        return {"status": "error", "message": f"Недостатньо коштів! Потрібно: {price} Ю"}
        
    cursor.execute(f"UPDATE users SET balance = balance - ?, {col} = 1 WHERE username = ?", (price, username))
    cursor.execute("UPDATE bank SET capital = capital + ? WHERE id = 1", (price,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/market_items")
def market_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, seller, item_name, price, description FROM market ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return [{"id": i[0], "seller": i[1], "item_name": i[2], "price": i[3], "description": i[4]} for i in items]

@app.post("/submit_market")
def submit_market(data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO market (seller, item_name, price, description) VALUES (?, ?, ?, ?)",
                   (data.get("seller"), data.get("item_name"), data.get("price"), data.get("description")))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/cancel_market")
def cancel_market(data: dict):
    item_id = data.get("item_id")
    seller = data.get("seller")
    is_admin = data.get("is_admin", False)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("DELETE FROM market WHERE id = ?", (item_id,))
    else:
        cursor.execute("DELETE FROM market WHERE id = ? AND seller = ?", (item_id, seller))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/buy_market")
def buy_market(data: dict):
    buyer = data.get("buyer")
    item_id = data.get("item_id")
    price = data.get("price")
    seller = data.get("seller")
    item_name = data.get("item_name")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (buyer,))
    res = cursor.fetchone()
    if not res or res[0] < price:
        conn.close()
        return {"status": "error", "message": "Недостатньо коштів на балансі!"}
        
    cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (price, buyer))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (price, seller))
    cursor.execute("DELETE FROM market WHERE id = ?", (item_id,))
    
    now = datetime.now().strftime("%H:%M")
    sys_msg = f"[РІНОК]: {buyer} придбав предмет '{item_name}' у продавця {seller} за {price:.1f} Ю!"
    cursor.execute("INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)", ("Система", sys_msg, now))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/citizens")
def citizens():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, user_id, role, balance, vip_level, permit_sell, permit_territory, permit_food, permit_weapons, permit_tools, email 
        FROM users ORDER BY role DESC, username ASC
    ''')
    users = cursor.fetchall()
    conn.close()
    return [{"username": u[0], "user_id": u[1], "role": u[2], "balance": u[3], "vip_level": u[4], 
             "permit_sell": u[5], "permit_territory": u[6], "permit_food": u[7], "permit_weapons": u[8], "permit_tools": u[9], "email": u[10]} for u in users]

@app.post("/submit_complaint")
def submit_complaint(data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    target = resolve_target_internal(cursor, data.get("target", ""))
    if not target:
        target = data.get("target")
    cursor.execute("INSERT INTO complaints (reporter, target, reason) VALUES (?, ?, ?)", 
                   (data.get("reporter"), target, data.get("reason")))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/complaints")
def get_complaints():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, reporter, target, reason FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "reporter": r[1], "target": r[2], "reason": r[3]} for r in rows]

# --- Адмін/Король ендпоінти ---
@app.post("/admin_action")
def admin_action(data: dict):
    action = data.get("action")
    target_raw = data.get("target", "")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    target = resolve_target_internal(cursor, target_raw) if target_raw else None

    if action == "set_role":
        if target:
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (data.get("role"), target))
    elif action == "delete":
        if target and target != data.get("admin_user"):
            cursor.execute("DELETE FROM users WHERE username = ?", (target,))
    elif action == "ban":
        if target and target != data.get("admin_user"):
            cursor.execute("SELECT role FROM users WHERE username = ?", (target,))
            res = cursor.fetchone()
            if not res or res[0] != "Адмін":
                cursor.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (target,))
    elif action == "unban":
        if target:
            cursor.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (target,))
    elif action == "units":
        mode = data.get("mode")
        amount = float(data.get("amount", 0))
        if target:
            if mode == "add":
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, target))
            elif mode == "sub":
                cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, target))
            elif mode == "set":
                cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (amount, target))
    elif action == "vip":
        if target:
            cursor.execute("UPDATE users SET vip_level = ? WHERE username = ?", (data.get("vip_level"), target))
    elif action == "permit":
        col = data.get("column")
        val = data.get("val")
        if target and col:
            cursor.execute(f"UPDATE users SET {col} = ? WHERE username = ?", (val, target))
    elif action == "capital":
        cursor.execute("UPDATE bank SET capital = ? WHERE id = 1", (data.get("capital"),))
    elif action == "royal_order":
        order_type = data.get("order_type")
        order_target = target if target else (target_raw if target_raw else "Усіх")
        text = data.get("text")
        now = datetime.now().strftime("%H:%M")
        cursor.execute("INSERT INTO royal_orders (type, target, text, timestamp) VALUES (?, ?, ?, ?)", (order_type, order_target, text, now))
        sys_msg = f"[{data.get('role').upper()}]: Оголошено {order_type} для {order_target}: {text}"
        cursor.execute("INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)", (data.get('role'), sys_msg, now))
    elif action == "taxes":
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Громадянин'")
        cnt = cursor.fetchone()[0]
        total = cnt * 50
        cursor.execute("UPDATE users SET balance = balance - 50 WHERE role = 'Громадянин' AND balance >= 50")
        cursor.execute("UPDATE users SET balance = balance + ? WHERE role = 'Король'", (total,))

    conn.commit()
    conn.close()
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)