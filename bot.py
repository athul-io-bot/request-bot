from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ------------------ CONFIG ------------------
API_ID = int(os.getenv("API_ID"))        # From my.telegram.org
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SPONSOR_CHANNEL = "sponsor_channel_username"  # Without @
DATABASE_CHANNEL = -1001234567890  # Your private channel ID (with -100)
# --------------------------------------------

bot = Client("movie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):
    args = message.command  # e.g. /start 12345
    if len(args) > 1:
        file_id = args[1]
        await message.reply_text(
            "👋 Welcome! Join our sponsor channel to continue:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📢 Join Sponsor", url=f"https://t.me/{SPONSOR_CHANNEL}")],
                 [InlineKeyboardButton("✅ I Joined", callback_data=f"check_sub:{file_id}")]]
            )
        )
    else:
        await message.reply_text("Send me a movie code or click a link in the channel.")
    

# Check subscription
@bot.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query):
    user = callback_query.from_user.id
    try:
        member = await client.get_chat_member(f"@{SPONSOR_CHANNEL}", user)
        if member.status in ["member", "administrator", "creator"]:
            await callback_query.message.edit("✅ Verified! Send me movie code now.")
        else:
            await callback_query.answer("❌ You must join sponsor channel first!", show_alert=True)
    except:
        await callback_query.answer("⚠️ Error checking subscription", show_alert=True)

# Fetch from database channel by movie code (message link or ID)
@bot.on_message(filters.private & filters.text)
async def fetch_file(client, message):
    query = message.text.strip()

    try:
        # Forward message from database channel
        msg = await client.get_messages(DATABASE_CHANNEL, int(query))
        await msg.copy(message.chat.id)
    except:
        await message.reply_text("❌ Movie not found! Please check the code.")

# Example inline button in public channel (manual use)
@bot.on_message(filters.command("post") & filters.user(123456789))  # only admin
async def post_to_channel(client, message):
    await client.send_message(
        "your_public_channel",
        "🎬 Movie Request:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Movie 720p", url="https://t.me/YourBot?start=12345")],
             [InlineKeyboardButton("Movie 1080p", url="https://t.me/YourBot?start=12346")]]
        )
    )

bot.run()
