import asyncio
import json
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import WebAppInfo, LabeledPrice
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "7615480625:AAGSwwPyMCfU_fvAu5qnSWCf-Ip_JnDCtJk"
PROVIDER_TOKEN = "YOUR_PROVIDER_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())  
router = Router()
dp.include_router(router)

# Подарки и их стоимость
GIFTS = {
    "mammoth": {"title": "Мамонт", "price": 1},
    "durov": {"title": "Фигурка Павла Дурова", "price": 2000},
    "dog": {"title": "Пёс", "price": 500},
    "mic": {"title": "Микрофон", "price": 300},
}

USER_STARS = {}  # Храним количество звезд у каждого пользователя

@router.message(Command("start", "webapp"))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть магазин 🎁", 
                web_app=WebAppInfo(url="https://vocococo.github.io/gifts/")
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("Открывай магазин и выбирай подарки! 🎁", reply_markup=keyboard)

@router.message(lambda message: message.web_app_data)
async def web_app_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    gift_id = data["gift_id"]
    price = int(data["price"])

    # Проверка на правильность суммы
    total_amount = price * 1  # сумма в самых маленьких единицах валюты

    payload = json.dumps({"gift_id": gift_id})

    await bot.send_invoice(
        chat_id=message.chat.id,
        title=GIFTS[gift_id]["title"],
        description="Оплата за виртуальный подарок 🎁",
        payload=payload,
        provider_token=PROVIDER_TOKEN,
        currency="XTR",
        prices=[LabeledPrice(label=GIFTS[gift_id]["title"], amount=total_amount)],
        start_parameter="gift-purchase"
    )

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id, ok=True  # Подтверждаем, что инвойс правильный
    )

@router.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: types.Message):
    payment = message.successful_payment
    user_id = message.from_user.id
    amount_paid = payment.total_amount / 1  # Преобразуем в нормальную валюту

    # Логика начисления виртуальных звезд или других действий
    user_stars = amount_paid  # Например, количество звезд равно сумме оплаты

    # Ответ пользователю
    await bot.send_message(
        chat_id=user_id,
        text=f"Спасибо за покупку! Все подарки хранятся у администратора."
    )
# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())