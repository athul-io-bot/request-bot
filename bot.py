from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ------------------ CONFIG ------------------
API_ID = int(os.getenv("API_ID"))        # from my.telegram.org
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SPONSOR_CHANNEL = "YourSponsorChannel"  # without @
DATABASE_CHANNEL = -1001234567890        # your private channel ID (-100..)
ADMIN_ID = 123456789                     # your Telegram user ID
# --------------------------------------------

bot = Client("movie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# 🔹 GROUP REQUEST HANDLER
@bot.on_message(filters.group & filters.text)
async def handle_group_request(client, message):
    query = message.text.lower().strip()

    try:
        # search movie in your database channel (by caption/filename)
        results = client.search_messages(DATABASE_CHANNEL, query, limit=1)
        async for file in results:
            movie_name = file.caption or "Requested Movie"
            msg_id = file.id

            # reply in group with inline button
            await message.reply_text(
                f"🎬 {movie_name}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📥 Download", url=f"https://t.me/{client.me.username}?start={msg_id}")]]
                )
            )
            return

        # no match found
        await message.reply_text("❌ Movie not found in database.")

    except Exception as e:
        print(e)
        await message.reply_text("⚠️ Error while searching. Try again later.")


# 🔹 START HANDLER (deep links)
@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):
    args = message.command  # e.g. ["/start", "12345"]
    if len(args) > 1:
        file_id = args[1]
        await message.reply_text(
            "👋 Welcome! Please join our sponsor channel to continue:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📢 Join Sponsor", url=f"https://t.me/{SPONSOR_CHANNEL}")],
                 [InlineKeyboardButton("✅ I Joined", callback_data=f"check_sub:{file_id}")]]
            )
        )
    else:
        await message.reply_text("Send a movie name in group to get a link.")


# 🔹 SPONSOR CHECK + FILE SEND
@bot.on_callback_query(filters.regex(r"check_sub:(.*)"))
async def check_subscription(client, callback_query):
    user = callback_query.from_user.id
    file_id = callback_query.data.split(":")[1]

    try:
        member = await client.get_chat_member(f"@{SPONSOR_CHANNEL}", user)
        if member.status in ["member", "administrator", "creator"]:
            await callback_query.message.edit("✅ Verified! Fetching your movie...")
            try:
                msg = await client.get_messages(DATABASE_CHANNEL, int(file_id))
                await msg.copy(callback_query.message.chat.id)
            except:
                await callback_query.message.reply_text("❌ File not found in database.")
        else:
            await callback_query.answer("❌ You must join sponsor channel first!", show_alert=True)
    except:
        await callback_query.answer("⚠️ Error checking subscription", show_alert=True)


# 🔹 ADMIN COMMAND TO POST DIRECTLY (optional)
@bot.on_message(filters.command("post") & filters.user(ADMIN_ID))
async def post_to_channel(client, message):
    args = message.text.split(" ", 2)
    if len(args) < 3:
        return await message.reply_text("Usage: /post <msg_id> <movie name>")
    
    msg_id, movie_name = args[1], args[2]

    await client.send_message(
        "your_public_channel_username",  # replace with your channel username
        f"🎬 {movie_name}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📥 Download", url=f"https://t.me/{client.me.username}?start={msg_id}")]]
        )
    )


bot.run()
