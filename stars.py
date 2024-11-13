import sqlite3

from aiogram import F, Router, html, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.formatting import (Bold, HashTag, as_key_value, as_list,
                                      as_marked_section)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.refund_star_payment import RefundStarPayment
from database import create_user, get_lottery, get_prize_lottery, get_user, give_stars, get_one_relevant_lottery
from icecream import ic
from aiogram.exceptions import TelegramBadRequest

router = Router()

@router.callback_query(F.data == 'start')
@router.message(CommandStart())
async def first_message(message: types.Message):
    
    user = get_user(message.from_user.id)
    if not user:
        created_user = create_user(message.from_user.id)
        if not created_user['ok']:
            await message_or_callback(
                message, 
                f"🥺 Ох, кажется, что-то пошло не так!\n\n🚫 К сожалению, произошла ошибка при регистрации. Пожалуйста, попробуйте снова чуть позже. "
                )
            return
    
    active_lottery_ucode = get_one_relevant_lottery()[0]
    ic(active_lottery_ucode)
    # give_stars(message.from_user.id, 100)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Участвовать", callback_data=f'participate_{active_lottery_ucode}')
    
    lottery = get_lottery(active_lottery_ucode)
    prize_stars = lottery[3]
    
    await message_or_callback(message, f"👋 Привет! Добро пожаловать в {html.bold("Звездную Лотерею")}!\n\n"
f"🌟 Участвуй в нашей увлекательной лотерее и получай шанс выиграть {html.bold(f"{prize_stars} звезд")}! \n\n"
f"✨ Чтобы участвовать, тебе нужно зарегистрироваться (это займет всего пару секунд) и {html.bold(f"купить несколько звёзд")}. \n"
f"{html.blockquote(f"Чем больше поставишь, тем {html.bold("выше шанс")} на выигрыш.")}\n\n"
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
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ 1", callback_data=f'pay_1_{ucode}', pay=True) #! поменять на 5 звезд (1 => 5)
    builder.button(text="⭐ 15", callback_data=f'pay_15_{ucode}', pay=True)
    builder.button(text="⭐ 25", callback_data=f'pay_25_{ucode}', pay=True)
    builder.button(text="⭐ 35", callback_data=f'pay_35_{ucode}', pay=True)
    builder.button(text="Отменить", callback_data="start")
    builder.adjust(2,2,1)
    
    user = get_user(callback.from_user.id)
    ic(user)
    if user[2] >= 1:
        return await message_or_callback(callback, "🌟 Ты уже участник Звездной Лотереи! 🌟\n\n"
"✨ Твой баланс: 10 звезд! ✨\n"
"🚀 Следи за розыгрышами, чтобы узнать, повезло ли тебе!")
    
    await message_or_callback(callback, "🎉 Отлично! Мы рады, что ты решил(а) поучаствовать в Звездной Лотерее! \n\n"
"✨ Чтобы стать участником и получить шанс выиграть 10 звезд, просто нажми на кнопку ниже и оплати звезды. \n\n"
"🚀 Удачи в розыгрыше!", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("pay_"))
async def send_invoice_handler(callback: types.CallbackQuery):
    data = callback.data.split("_")
    amount = int(data[1])
    ucode = data[2]
    
    lottery = get_lottery(ucode)
    total_win = lottery[3]
    
    prices = types.LabeledPrice(label=f"Оплатить {amount} ⭐", amount=amount)
    await callback.message.answer_invoice(title="Участие в лотерее", description=f"Регистрация в лотерее с призом {total_win} ⭐",
                                 prices=[prices], provider_token="", payload=f"buy_stars_{amount}_{ucode}",
                                 currency="XTR")

@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    ic(pre_checkout_query.from_user.id)
    user = get_user(pre_checkout_query.from_user.id)
    ic(pre_checkout_query.invoice_payload)
    ic(user)
    if user:
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False, error_message="Так надо.")
    
@router.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    
    participant = 1
    ic(message.successful_payment.total_amount)
    
    give_stars(message.from_user.id, message.successful_payment.total_amount)
    
    await message.answer(
        f"Мы рады сообщить, что вы стали участником № {participant} нашего мероприятия!\n\n 🙌 Благодарим вас за вашу активность и интерес! 💖\n\n"
        )
    
    await message.answer(f"payment-successful. ID of operation: <code>{message.successful_payment.telegram_payment_charge_id}</code>")
    
    
async def message_or_callback(type, message, reply_markup=None, message_effect_id=None):
    if isinstance(type, types.Message):
        await type.answer(message, reply_markup=reply_markup, message_effect_id=message_effect_id)
    elif isinstance(type, types.CallbackQuery):
        await type.message.edit_text(message, reply_markup=reply_markup)
    else:
        raise TypeError("Неверный тип объекта: ожидается Message или CallbackQuery")
    
    
    
@router.message(Command("refund-test-payment-charge-id-callback-query-callback-query-query-effect"))
async def cmd_refund(
    message: types.Message,
    command: CommandObject,
):
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(
            text="✨ <b>Хочешь вернуть свои звездочки?</b> ✨\n\n"
"🌟 Чтобы вернуть средства за покупку, введи команду:\n\n"
"<code>/refund КОД</code>\n\n"
"⭐️ КОД - это идентификатор транзакции. Ты можешь найти его:\n\n"
"- После завершения платежа\n"
"- В разделе \"Звёзды\" в приложении Telegram.\n\n"
"🚀 Удачи!")
        return
    try:

        await message.bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            text="Возврат произведён успешно. Потраченные звёзды уже вернулись на ваш счёт в Telegram."
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = "😔 Ох, такого кода покупки мы не нашли! \n\n"
            "🤔 Пожалуйста, проверь, правильно ли ты ввёл код. Может быть, ты ошибся в написании? "
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = "🌟 Ты уже получил(а) возврат средств за эту покупку! 🌟\n\n"
            "💰 Деньги вернулись на твой счет. \n\n"
            "🎉 Надеемся, ты снова решишь поучаствовать в Звездной Лотерее!"
        else:
            # При всех остальных ошибках – такой же текст,
            # как и в первом случае
            text = "😔 Ох, такого кода покупки мы не нашли! \n\n"
            "🤔 Пожалуйста, проверь, правильно ли ты ввёл код. Может быть, ты ошибся в написании? "
        await message.answer(text)
        return