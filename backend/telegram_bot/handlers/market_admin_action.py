# telegram_bot/handlers/market_admin_action.py
# Admin se Matka market temporary ON/OFF karne ke liye single file.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

try:
    from bson import ObjectId  # optional, not required here
except Exception:
    ObjectId = None

from db.mongo import db
from config import globals as G

ADMIN_CHAT_ID = getattr(G, "ADMIN_CHAT_ID", None)

MARKETS = [
    "SRIDEVI_DAY", "SRIDEVI_NIGHT", "TIME_BAZAR_DAY", "MAIN_BAZAR_NIGHT",
    "MADHUR_DAY", "MADHUR_NIGHT", "MILAN_DAY", "MILAN_NIGHT",
    "RAJDHANI_DAY", "RAJDHANI_NIGHT", "SUPREME_DAY", "SUPREME_NIGHT",
    "KALYAN_DAY", "KALYAN_NIGHT"
]

COLLECTION = "market_settings"
DOC_KEY = "matka_disabled_markets"

async def get_disabled_markets():
    doc = await db[COLLECTION].find_one({"key": DOC_KEY})
    return doc.get("disabled_markets", []) if doc else []

async def set_market_disabled(market_key: str, disabled: bool):
    if disabled:
        await db[COLLECTION].update_one(
            {"key": DOC_KEY},
            {"$addToSet": {"disabled_markets": market_key}},
            upsert=True
        )
    else:
        await db[COLLECTION].update_one(
            {"key": DOC_KEY},
            {"$pull": {"disabled_markets": market_key}},
            upsert=True
        )

async def is_market_disabled(market_key: str):
    disabled = await get_disabled_markets()
    return market_key in disabled

async def build_market_admin_keyboard():
    disabled = await get_disabled_markets()
    rows = []
    for market in MARKETS:
        is_off = market in disabled
        label = f"{'🔴 OFF' if is_off else '🟢 ON'} {market}"
        action = "ON" if is_off else "OFF"
        rows.append([InlineKeyboardButton(label, callback_data=f"MARKET:{action}:{market}")])
    rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="MARKET:REFRESH")])
    return InlineKeyboardMarkup(rows)

async def show_market_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if ADMIN_CHAT_ID and uid != ADMIN_CHAT_ID:
        if update.callback_query:
            await update.callback_query.answer("Not authorized", show_alert=True)
        else:
            await update.message.reply_text("❌ You are not authorized.")
        return

    keyboard = await build_market_admin_keyboard()
    text = "⚙️ *Matka Market Control*\n\nMarket ko ON/OFF karne ke liye button press karo."

    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def market_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    if ADMIN_CHAT_ID and uid != ADMIN_CHAT_ID:
        return await q.answer("❌ You are not authorized.", show_alert=True)

    data = q.data or ""

    if data == "MARKET:REFRESH":
        return await show_market_admin(update, context)

    parts = data.split(":")
    if len(parts) != 3:
        return await q.message.reply_text("⚠️ Invalid market action.")

    _, action, market_key = parts

    if market_key not in MARKETS:
        return await q.message.reply_text("⚠️ Invalid market name.")

    if action == "OFF":
        await set_market_disabled(market_key, True)
        status_text = f"🔴 {market_key} OFF kar diya."
    elif action == "ON":
        await set_market_disabled(market_key, False)
        status_text = f"🟢 {market_key} ON kar diya."
    else:
        return await q.message.reply_text("⚠️ Invalid action.")

    keyboard = await build_market_admin_keyboard()
    await q.message.edit_text(
        f"⚙️ *Matka Market Control*\n\n{status_text}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# FastAPI/frontend ke liye helper endpoint me use kar sakte ho:
# @router.get('/api/games/matka/disabled-markets')
# async def disabled_markets_api():
#     return {'disabled_markets': await get_disabled_markets()}