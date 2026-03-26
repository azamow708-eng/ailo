from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from db import init_db, set_language, get_user, update_subscription, give_referral_bonus
from payments import create_invoice
from config import API_TOKEN, CHANNEL_USERNAME, ADMINS
from datetime import datetime, timedelta

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

init_db()

# Launch / discount config
LAUNCH_DATE = datetime(2026,3,26)
DISCOUNT_DAYS = 4
DISCOUNT_PERCENT = 40
PLAN_PRICES = {"1d":1, "7d":6, "30d":18}

def get_price(plan):
    price = PLAN_PRICES[plan]
    now = datetime.now()
    if plan=="30d" and now <= LAUNCH_DATE + timedelta(days=DISCOUNT_DAYS):
        price = round(price*(1-DISCOUNT_PERCENT/100),2)
        return price, True
    return price, False

# Languages
lang_kb = InlineKeyboardMarkup()
lang_kb.add(
    InlineKeyboardButton("ðŸ‡·ðŸ‡º Ð ÑƒÑÑÐºÐ¸Ð¹", callback_data="lang_ru"),
    InlineKeyboardButton("ðŸ‡¬ðŸ‡§ English", callback_data="lang_en")
)

def pay_keyboard(lang="en"):
    kb = InlineKeyboardMarkup()
    for plan in ["1d","7d","30d"]:
        price, discount = get_price(plan)
        text = f"{plan} - ${price}" if lang=="en" else f"{plan} - ${price} ({plan})"
        if discount:
            text += " âš¡ï¸Discount!" if lang=="en" else " âš¡ï¸ÐÐºÑ†Ð¸Ñ!"
        kb.add(InlineKeyboardButton(text=text, callback_data=f"pay_{plan}"))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Select your language / Ð’Ñ‹Ð±ÐµÑ€Ð¸Ñ‚Ðµ ÑÐ·Ñ‹Ðº:", reply_markup=lang_kb)

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def set_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split("_")[1]
    set_language(callback_query.from_user.id, lang)
    await callback_query.answer()
    
    # Forced subscription
    chat_member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", callback_query.from_user.id)
    if chat_member.status in ["member","administrator","creator"]:
        text = "âœ… Subscribed! Access granted." if lang=="en" else "âœ… ÐŸÐ¾Ð´Ð¿Ð¸ÑÐ°Ð½Ñ‹! Ð”Ð¾ÑÑ‚ÑƒÐ¿ Ð¾Ñ‚ÐºÑ€Ñ‹Ñ‚."
        await bot.send_message(callback_query.from_user.id, text, reply_markup=pay_keyboard(lang))
    else:
        text = f"âš ï¸ You must subscribe to @{CHANNEL_USERNAME} first." if lang=="en" else f"âš ï¸ Ð¡Ð½Ð°Ñ‡Ð°Ð»Ð° Ð¿Ð¾Ð´Ð¿Ð¸ÑˆÐ¸Ñ‚ÐµÑÑŒ Ð½Ð° @{CHANNEL_USERNAME}."
        await bot.send_message(callback_query.from_user.id, text)

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def payment(callback_query: types.CallbackQuery):
    plan = callback_query.data.split("_")[1]
    price, _ = get_price(plan)
    invoice = create_invoice(callback_query.from_user.id, amount_usd=price, plan=plan)
    if invoice:
        await bot.send_message(callback_query.from_user.id, f"Payment link: {invoice['invoice_url']}")
    else:
        await bot.send_message(callback_query.from_user.id, "Payment error!")
