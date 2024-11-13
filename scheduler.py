import random

from aiogram import Bot, Router, html
from icecream import ic

from database import (clear_lottery, clear_star, close_lottery, get_full_participants, get_participants,
                      get_prize_lottery, get_relevants_lottery)

router = Router()

# async 

async def newsletter(ucode, bot: Bot = None, 
                     winner: int = None, qty_users: int = 0):
    if not winner: 
        return False

    users = get_full_participants(ucode)
    lottery = get_prize_lottery(ucode)

    for user in users:

        chance = int(user[2] / qty_users * 100)

        text = f"Поздравляем! У нас есть {html.bold("победитель")}! 🎉\n\n"\
f"Сегодня счастливчиком стал {html.link("Пользователь", f"tg://user?id={winner}")}, который выиграл всю сумму, составившую {lottery} ⭐! \n\n"\
f"Кстати! Ваш {html.bold("шанс")} на выигрыш составил: {chance}%. Всего мест: {qty_users}, Вы занимаете {user[2]}.\n\n"\
"Спасибо всем участникам за вашу веру в наше честное распределение. Следите за нашими следующими мероприятиями и не упустите шанс стать следующим победителем!"

        await bot.send_message(user[1], text, message_effect_id="5046509860389126442")
    
    return True
    

async def get_winner_lottery(ucode: str, bot: Bot = None) -> int:
    participants = get_participants(ucode)
    # ic(participants)
    
    prize_lottery = get_prize_lottery(ucode)
    sum_lottery = 0
    users_lottery = {}
    for user in participants:
        # ic(user)
        users_lottery[f"{user[1]}"] = user[2]
        sum_lottery += user[2]
    # ic(users_lottery)
    ic(sum_lottery, prize_lottery)
    
    if sum_lottery < prize_lottery * 1.3:
        pass
    
    weighted_users = []
    ic(users_lottery)
    for user, amount in users_lottery.items():
        ic(user, amount)
        
        weighted_users.extend([int(user)] * amount)  # Добавляем пользователя количество раз, равное его пожертвованию
        
    if not weighted_users:
        ic("No participants for lottery")
        return False
    
    qty_users = len(weighted_users)
    
    
    ic(weighted_users)
    selected_user = random.choice(weighted_users)
    
    
    await newsletter(ucode, bot=bot, winner=selected_user, qty_users=qty_users)
    clear_star(ucode)
    clear_lottery(ucode)
    close_lottery(ucode)
    
    ic(selected_user)
    return selected_user

async def check_active_lottery(lottery_ucode: str = None, bot: Bot = None):

    ucodes = get_relevants_lottery()
    
    for u in ucodes:
        await get_winner_lottery(u[0], bot=bot)
