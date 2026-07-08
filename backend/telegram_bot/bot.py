import os
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, Application
# from handlers.dm_handler import handle_deposit_buttons, admin_deposit_action, admin_withdraw_action
# from handlers.reg_handler import start_update_account
# from handlers.helper import handle_play_summary
# from ui.registration_box import build_admin_box
# from db.balance_handler_db import balance_handler
# from db.user_handler_db import user_details_handler, pagination_handler, user_view_handler
# from db.msg_handler_db import handle_admin_message_action

BOT_TOKEN   = "7586206872:AAE_4msuKoeguB5_UEgyeypX1-JdYxW0ecA"
# BOT_TOKEN=os.getenv("BOT_TOKEN","PASTE_TOKEN_HERE")
ADMIN_CHAT_ID=int(os.getenv("ADMIN_CHAT_ID","6945487333"))

bot=Bot(token=BOT_TOKEN)

async def start(update,context):
    param=context.args[0] if context.args else None
    if param=="deposit":
        return await handle_deposit_buttons(update,context)
    if param=="update":
        return await start_update_account(update,context)
    await update.message.reply_text("🎰 Welcome to GOLD365\nUse menu buttons to continue.")

async def update_upi(update,context):
    query=update.callback_query
    if query:
        await query.answer()
        uid=query.from_user.id
        if uid!=ADMIN_CHAT_ID:
            return await query.message.reply_text("❌ You are not authorized.")
        G.upi_update_sessions[uid]="waiting_for_upi"
        return await query.message.reply_text("📝 Please enter new UPI ID:",parse_mode="Markdown")
    uid=update.effective_user.id
    if uid!=ADMIN_CHAT_ID:
        return await update.message.reply_text("❌ You are not authorized.")
    G.upi_update_sessions[uid]="waiting_for_upi"
    await update.message.reply_text("📝 Please enter new UPI ID:",parse_mode="Markdown")

async def text_handler(update,context):
    uid=update.effective_user.id
    text=update.message.text
    if G.upi_update_sessions.get(uid)=="waiting_for_upi":
        G.UPI_ID=text.strip()
        G.upi_update_sessions.pop(uid,None)
        return await update.message.reply_text(f"✅ UPI updated:\n`{G.UPI_ID}`",parse_mode="Markdown")
    await update.message.reply_text("Please use buttons.")

async def on_startup(app:Application):
    G.BOT=app.bot
    print("✅ Telegram payment/admin bot started")


async def admin(update,context):
    uid=update.effective_user.id
    if uid!=ADMIN_CHAT_ID:
        return await update.message.reply_text("❌ You are not authorized.")
    await update.message.reply_text(
        "👑 Admin Panel\n\nChoose action:",
        reply_markup=None
    )

# async def start_bot_background():
#     app=ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

#     # app.add_handler(CommandHandler("start",start))
#     # app.add_handler(CallbackQueryHandler(handle_play_summary,pattern="^HELP:HOW_PLAY$"))
#     # app.add_handler(CallbackQueryHandler(build_admin_box,pattern="^ADMIN:(ADMIN_LOGIN|TODAY_OFFER|BALANCE|USER_DETAILS|MAIN|GAME_START|GAME_STOP|MATCH_ODDS|TOSS_WINNER)$"))
#     # app.add_handler(CallbackQueryHandler(update_upi,pattern="^ADMIN:UPDATE_UPI$"))
#     # app.add_handler(CallbackQueryHandler(admin_deposit_action,pattern="^(DEPAPP|DEPREJ):"))
#     # app.add_handler(CallbackQueryHandler(admin_withdraw_action,pattern="^(WAPP|WREJ):"))
#     # app.add_handler(CallbackQueryHandler(balance_handler,pattern="^BALANCE:"))
#     # app.add_handler(CallbackQueryHandler(user_details_handler,pattern="^USER_DETAILS:"))
#     # app.add_handler(CallbackQueryHandler(handle_admin_message_action,pattern="^TODAY_OFFER:"))
#     # app.add_handler(CallbackQueryHandler(pagination_handler,pattern="^USER_PAGE:"))
#     # app.add_handler(CallbackQueryHandler(user_view_handler,pattern="^USER_VIEW:"))
#     # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))

#     await app.initialize()
#     await app.start()
#     await app.updater.start_polling()
#     BOT=app.bot
#     print("✅ Telegram bot started from FastAPI")
#     return app

async def start_bot_background():
    app=ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("admin",admin))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("✅ Telegram bot started from FastAPI")
    return app