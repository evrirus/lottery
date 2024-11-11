import random

from aiogram import Bot, Router, html
from icecream import ic

from database import (clear_star, get_full_participants, get_participants,
                      get_prize_lottery, get_relevants_lottery)

router = Router()


async def newsletter(ucode, bot: Bot = None):
    ic(ucode, bot)
    
    users = get_full_participants(ucode)
    lottery = get_prize_lottery(ucode)
    for user in users:
        ic(user[1])
        
        text = f"Поздравляем! У нас есть {html.bold("победитель")}! 🎉\n\n"\
f"Сегодня счастливчиком стал {html.link("Пользователь", f"tg://user?id={user[1]}")}, который выиграл всю сумму, составившую {lottery} ⭐! \n\n"\
"Спасибо всем участникам за ваши пожертвования и поддержку. Следите за нашими следующими мероприятиями и не упустите шанс стать следующим победителем!"

        await bot.send_message(user[1], text, message_effect_id="5104841245755180586" )
    

async def get_winner_lottery(ucode: str, bot: Bot = None) -> int:
    participants = get_participants(ucode)
    ic(participants)
    
    prize_lottery = get_prize_lottery(ucode)
    sum_lottery = 0
    users_lottery = {}
    for user in participants:
        ic(user)
        users_lottery[f"{user[1]}"] = user[2]
        sum_lottery += user[2]
    ic(users_lottery)
    ic(sum_lottery, prize_lottery)
    
    if sum_lottery < prize_lottery:
        pass
    
    weighted_users = []
    # ic(users_lottery.items())
    for user, amount in users_lottery.items():
        ic(user, amount)
        
        weighted_users.extend([int(user)] * amount)  # Добавляем пользователя количество раз, равное его пожертвованию
        
    if not weighted_users:
        ic("No participants for lottery")
        return False
    
    ic(weighted_users)
    selected_user = random.choice(weighted_users)
    clear_star(ucode)
    await newsletter(ucode, bot=bot)
    ic(selected_user)
    return selected_user

async def check_active_lottery(lottery_ucode: str = None, bot: Bot = None):
    ic(bot)
    ucodes = get_relevants_lottery()
    ic(ucodes)
    
    for u in ucodes:
        await get_winner_lottery(u[0], bot=bot)
    
    # dict_users_participants = {}
    # for u in ucodes:
        
    #     participants = get_participants(u[0])
    #     dict_users_participants[u[0]] = []
        
    #     for user in participants:
    #         dict_users_participants[u[0]].append({"tg": user[1],
    #                                               "stars": user[2]})

    # for ucode_lottery in dict_users_participants:
    #     sum_stars = 0
    #     for users in dict_users_participants[ucode_lottery]:
    #         sum_stars += users['stars']
            
    #     prize_lottery = get_prize_lottery(ucode_lottery)
        
    #     ic(sum_stars)
    #     ic(prize_lottery)
    #     if sum_stars >= prize_lottery:
    #         pass

    # ic(dict_users_participants)