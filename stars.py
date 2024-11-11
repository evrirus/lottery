import sqlite3

from aiogram import F, Router, html, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.formatting import (Bold, HashTag, as_key_value, as_list,
                                      as_marked_section)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.refund_star_payment import RefundStarPayment
from database import create_user, get_user, give_stars, get_one_relevant_lottery
from icecream import ic

router = Router()

@router.message(CommandStart())
async def first_message(message: types.Message):
    
    user = get_user(message.from_user.id)
    if not user:
        created_user = create_user(message.from_user.id)
        if not created_user['ok']:
            await message.answer(f"🥺 Ох, кажется, что-то пошло не так!\n\n🚫 К сожалению, произошла ошибка при регистрации. Пожалуйста, попробуйте снова чуть позже. ")
            return
    
    active_lottery_ucode = get_one_relevant_lottery()[0]
    ic(active_lottery_ucode)
    # give_stars(message.from_user.id, 100)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Участвовать", callback_data=f'participate_{active_lottery_ucode}')
    
    prize_stars = 10
    min_stars_buy = 1
    
    await message.answer(f"👋 Привет! Добро пожаловать в {html.bold("Звездную Лотерею")}!\n\n"
f"🌟 Участвуй в нашей увлекательной лотерее и получай шанс выиграть {html.bold(f"{prize_stars} звезд")}! \n\n"
f"✨ Чтобы участвовать, тебе нужно зарегистрироваться (это займет всего пару секунд) и {html.bold(f"купить {min_stars_buy} звёзд")}. \n\n"
"⏳ Каждые несколько дней мы проводим розыгрыш, и один счастливчик получит главный приз! \n\n"
"🚀 Присоединяйся к нам и испытай удачу! \n\n"
f"{html.bold("Как участвовать")}:\n\n"
"1. Зарегистрируйся в боте.\n"
"2. Купи звезды.\n"
"3. Следи за розыгрышем! \n\n"
f"{html.bold("Удачи!")}", reply_markup=builder.as_markup(), message_effect_id="5104841245755180586")


# @router.message(Command(commands=['participate', 'участвовать']))
@router.callback_query(F.data.startswith('participate_'))
async def participate(callback: types.CallbackQuery):
    
    data = callback.data
    ucode = data[len('participate_'):]
    ic(ucode)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Оплатить 1 ⭐", callback_data=f'pay_1_{ucode}', pay=True)
    
    await message_or_callback(callback, "🎉 Отлично! Мы рады, что ты решил(а) поучаствовать в Звездной Лотерее! \n\n"
"✨ Чтобы стать участником и получить шанс выиграть 10 звезд, просто нажми на кнопку ниже и оплати 1 звезду. \n\n"
"🚀 Удачи в розыгрыше!", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("pay_"))
async def send_invoice_handler(callback: types.CallbackQuery):
    data = callback.data.split("_")
    amount = int(data[1])
    ucode = data[2]
    
    prices = types.LabeledPrice(label=f"Оплатить {amount} ⭐", amount=amount)
    await callback.message.answer_invoice(title="Участие в лотерее", description="Регистрация в лотерее с призом 10 ⭐",
                                 prices=[prices], provider_token="", payload=f"buy_stars_{amount}_{ucode}",
                                 currency="XTR")

@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    user = get_user(pre_checkout_query.from_user.id)
    ic(pre_checkout_query.invoice_payload)
    
    if user[2] >= 1:
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False)
    
@router.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    
    participant = 1
    
    await message.answer(
        f"Мы рады сообщить, что вы стали участником № {participant} нашего мероприятия! 🙌 Благодарим вас за вашу активность и интерес! 💖\n\n"
        )
    
    await message.answer(f"payment-successful. ID of operation: {message.successful_payment.telegram_payment_charge_id}")
    
    
async def message_or_callback(type, message, reply_markup=None, message_effect_id=None):
    if isinstance(type, types.Message):
        await type.answer(message, reply_markup=reply_markup, message_effect_id=message_effect_id)
    elif isinstance(type, types.CallbackQuery):
        await type.message.edit_text(message, reply_markup=reply_markup)
    else:
        raise TypeError("Неверный тип объекта: ожидается Message или CallbackQuery")