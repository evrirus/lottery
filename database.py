import sqlite3
from icecream import ic
DATABASE_PATH = "stars.db"

def find_one(q: str, data: tuple=""):
    connection = sqlite3.connect(DATABASE_PATH)
    cur = connection.cursor()
    
    cur.execute(q, data)
    result = cur.fetchone()
    
    connection.close()
    
    if result:
        return result
    return None

def find_many(q: str, data: tuple=""):
    connection = sqlite3.connect(DATABASE_PATH)
    cur = connection.cursor()
    
    cur.execute(q, data)
    result = cur.fetchall()
    # ic(result, q, data)
    
    connection.close()
    
    return result

def commit(q: str, data: tuple=""):
    connection = sqlite3.connect(DATABASE_PATH)
    cur = connection.cursor()
    
    cur.execute(q, data)
    connection.commit()
    connection.close()

def create_user(telegram_id: int, stars: int = 0):
    data = (telegram_id, stars)
    ok = find_one("INSERT INTO users (telegram_id, stars) VALUES (?, ?)", data)
    if ok:
        return {'ok': True, 'telegram_id': telegram_id}
    return {'ok': False, 'telegram_id': telegram_id}

def get_user(telegram_id: int):
    user = find_one("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))

    if user:
        return True
    return False

def give_stars(telegram_id: int, amount: int):
    return commit("UPDATE users SET stars=stars+? WHERE telegram_id = ?", (amount, telegram_id,))
    
def get_participants(lottery_ucode: str):
    return find_many("SELECT * FROM users WHERE ucode_lottery = ? AND stars >= 1", (lottery_ucode,))

def get_full_participants(lottery_ucode: str):
    return find_many("SELECT * FROM users WHERE ucode_lottery = ?", (lottery_ucode,))

def get_relevants_lottery():
    return find_many("SELECT ucode FROM lottery WHERE relevant >= 1")

def get_one_relevant_lottery():
    return find_one("SELECT ucode FROM lottery WHERE relevant >= 1")

def get_prize_lottery(lottery_ucode: str):
    ic(lottery_ucode)
    return find_one("SELECT prize FROM lottery WHERE ucode = ?", (lottery_ucode,))[0]

def clear_star(lottery_ucode):
    return commit("UPDATE users SET stars=0 WHERE ucode_lottery = ?", (lottery_ucode,))