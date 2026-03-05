import asyncio
import os
import logging
import mimetypes
from aiohttp import web
from pyrogram import Client, filters

# Python 3.14+ compatibility for Pyrogram
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Set logging levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pyrogram log reduction
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# --- CONFIGURATION ---
API_ID = 35816137
API_HASH = "f457c1c04f3fba7fd789f9e738143c6f"
DOMAIN = "https://tele.cmovie.xyz"
PORT = 8080
DOWNLOAD_DIR = "./vps_downloads"

# Create download directory if not exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- CLIENT SETUP WITH LOCAL API ---
app = Client(
    "direct_dl_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=False,
    sleep_threshold=120,
    workers=200
)

@app.on_message(filters.command("link") & filters.me)
async def generate_link(client, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.reply_text("❌ කරුණාකර ෆයිල් එකකට හෝ වීඩියෝ එකකට Reply කර `/link` ලෙස යවන්න.")
        return

    media = message.reply_to_message
    file_name = "download_file"
    
    media_obj = getattr(media, media.media.value)
    if media_obj and hasattr(media_obj, 'file_name') and media_obj.file_name:
        file_name = media_obj.file_name
    
    file_name = file_name.replace(" ", "_")
    chat_id = str(message.chat.id)
    msg_id = media.id

    link = f"{DOMAIN}/dl/{chat_id}/{msg_id}/{file_name}"
    
    await message.reply_text(
        f"🚀 **Fast Link Ready (Local API Mode)**\n\n"
        f"📁 **File:** `{file_name}`\n"
        f"🔗 **Link:** `{link}`\n\n"
        f"⚠️ *ඩවුන්ලෝඩ් එක අවසන් වූ පසු ෆයිල් එක VPS එකෙන් මැකී යනු ඇත.*",
        disable_web_page_preview=True
    )

# --- Web Server ---
routes = web.RouteTableDef()

@routes.get('/dl/{chat_id}/{msg_id}/{filename}')
async def download_handler(request):
    try:
        chat_id = int(request.match_info['chat_id'])
        msg_id = int(request.match_info['msg_id'])
        filename = request.match_info['filename']
    except ValueError:
        return web.Response(status=400, text="Invalid Parameters")

    try:
        message = await app.get_messages(chat_id, msg_id)
        if not message or message.empty:
            return web.Response(status=404, text="Message not found")
    except Exception as e:
        return web.Response(status=500, text=f"Telegram Error: {str(e)}")

    # VPS එකේ තාවකාලිකව සේව් වන ගොනුවේ නම
    file_path = os.path.join(DOWNLOAD_DIR, f"{msg_id}_{filename}")

    # 1. පයිල් එක දැනටමත් VPS එකේ නැත්නම් ඩවුන්ලෝඩ් කරන්න
    if not os.path.exists(file_path):
        logger.info(f"Downloading {filename} for streaming...")
        try:
            await app.download_media(message, file_name=file_path)
        except Exception as e:
            return web.Response(status=500, text=f"Download Error: {str(e)}")

    # 2. FileResponse හරහා පරිශීලකයාට ලබා දීම
    response = web.FileResponse(file_path)
    
    # 3. AUTO-DELETE: යවා අවසන් වූ විගස මැකීමට cleanup function එකක්.
    async def cleanup_file(request, resp):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file: {e}")

    # Response එක prepare කරන විට cleanup function එක add කිරීම
    request.app.on_response_prepare.append(cleanup_file)
    
    return response

async def start_services():
    print("----------------------------------------")
    print("Starting Telegram Client...")
    await app.start()

    print("Starting Web Server...")
    web_app = web.Application(client_max_size=0)
    web_app.add_routes(routes)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    me = await app.get_me()
    print(f"DONE! Logged in as: {me.first_name}")
    print(f"WEB SERVER RUNNING ON PORT {PORT}")
    print(f"DOWNLOAD CACHE: {os.path.abspath(DOWNLOAD_DIR)}")
    print("----------------------------------------")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Fatal Error: {e}")


