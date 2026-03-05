import asyncio

# Python 3.14+ වලදී Pyrogram import කිරීමේදී එන "no current event loop" දෝෂය මග හැරීමට මෙම කොටස එකතු කළ යුතුය.
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import logging
import mimetypes
from aiohttp import web

# Pyrogram වල "TgCrypto is missing!" නිවේදනය සැඟවීම
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.crypto").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.ERROR)

from pyrogram import Client, filters

# ඔබගේ API විස්තර
API_ID = 35816137
API_HASH = "f457c1c04f3fba7fd789f9e738143c6f"

DOMAIN = "https://tele.cmovie.xyz"
PORT = 8080

# Pyrogram Client - Userbot ලෙස (QR කේතය හරහා ලොග් වීමට)
app = Client(
    "direct_dl_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=False,
    sleep_threshold=60, # Limit එක පැනීම වැළැක්වීමට
    workers=100        # Concurrent connections වැඩි කිරීම
)

# ඕනෑම තැනකදී (Group, Channel, Private) ඔබට පමණක් (/link) යැවූ විට වැඩ කරන ලෙස
@app.on_message(filters.command("link") & filters.me)
async def generate_link(client, message):
    print("Received /link command!") # Debug
    # ෆයිල් එකකට රිප්ලයි කර නොමැති නම්
    if not message.reply_to_message or not message.reply_to_message.media:
        print("No media found in reply.")
        await message.reply_text("කරුණාකර ෆයිල් එකකට හෝ වීඩියෝ එකකට Reply කර `/link` ලෙස යවන්න.")
        return

    media = message.reply_to_message
    print(f"Media found! Type: {media.media}")
    
    # ෆයිල් එකේ නම හඳුනා ගැනීම
    file_name = "download_file"
    if getattr(media, "document", None) and getattr(media.document, "file_name", None):
        file_name = media.document.file_name
    elif getattr(media, "video", None) and getattr(media.video, "file_name", None):
        file_name = media.video.file_name
    elif getattr(media, "audio", None) and getattr(media.audio, "file_name", None):
        file_name = media.audio.file_name

    # හිස්තැන් ඉවත් කිරීම
    file_name = file_name.replace(" ", "_")

    # chat id එක සහ message id එක ලබා ගැනීම (Log channel එකක් අවශ්‍ය නැත)
    chat_id = str(message.chat.id)
    msg_id = media.id

    # Direct URL එක සැකසීම (අගට ෆයිල් නම සහිතව)
    link = f"{DOMAIN}/dl/{chat_id}/{msg_id}/{file_name}"
    
    await message.reply_text(f"**Direct Download Link :**\n\n📥 [{file_name}]({link})\n\n🔗 ලින්ක් එක:\n`{link}`", disable_web_page_preview=True)


# Web Server කොටස (Aiohttp)
routes = web.RouteTableDef()

@routes.get('/dl/{chat_id}/{msg_id}/{filename}')
async def download_handler(request):
    try:
        chat_id = int(request.match_info['chat_id'])
        msg_id = int(request.match_info['msg_id'])
        filename = request.match_info['filename']
    except ValueError:
        return web.Response(status=400, text="Invalid Link")

    try:
        # අදාළ Chat එකෙන් Message එක ලබාගැනීම
        message = await app.get_messages(chat_id, msg_id)
        if not message or message.empty:
            return web.Response(status=404, text="File Not Found")
    except Exception as e:
         return web.Response(status=404, text=f"Message cannot be retrieved: {str(e)}")

    media = message.document or message.video or message.audio
    if not media:
        return web.Response(status=404, text="No Media Found")

    file_size = media.file_size
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    # Direct Download වීමට Headers සැකසීම
    headers = {
        "Content-Type": mime_type,
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(file_size),
    }

    response = web.StreamResponse(status=200, headers=headers)
    await response.prepare(request)

    # Telegram එකෙන් File එක stream කර කෙලින්ම Web Server එක හරහා යැවීම
    async for chunk in app.stream_media(message):
        try:
            await response.write(chunk)
        except Exception:
            break

    return response

async def start_services():
    print("Starting Telegram Client...")
    await app.start()
    
    print("Starting Web Server...")
    web_app = web.Application()
    web_app.add_routes(routes)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"Server runs on port {PORT}. Bot is ready!")
    
    # Keep the program running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Same loop that Pyrogram bound to at the top level
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print("Bot stopped")
