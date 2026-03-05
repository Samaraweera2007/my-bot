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
logging.getLogger("pyrogram.crypto").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.ERROR)

# --- CONFIGURATION ---
API_ID = 35816137
API_HASH = "f457c1c04f3fba7fd789f9e738143c6f"
DOMAIN = "https://tele.cmovie.xyz"
PORT = 8080
# ---------------------

app = Client(
    "direct_dl_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=False,
    sleep_threshold=60,
    workers=200  # Increased workers for high-speed parallel handling
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
        f"🚀 **High-Speed Link Ready!**\n\n"
        f"📁 **File:** `{file_name}`\n"
        f"🔗 **Link:** `{link}`\n\n"
        f"💡 **IDM** භාවිතා කරන්න. (Connections 32 දමා ගන්න)",
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

    media = message.document or message.video or message.audio or message.animation
    if not media:
        return web.Response(status=404, text="No Media Found")

    file_size = media.file_size
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    
    # Handle Range Requests (Crucial for Speed in IDM)
    range_header = request.headers.get("Range")
    start = 0
    end = file_size - 1
    
    if range_header:
        try:
            # Parse 'bytes=start-end'
            bytes_range = range_header.replace("bytes=", "").split("-")
            start = int(bytes_range[0])
            if bytes_range[1]:
                end = int(bytes_range[1])
        except Exception:
            pass

    content_length = end - start + 1
    
    headers = {
        "Content-Type": mime_type,
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(content_length),
        "Accept-Ranges": "bytes",
        "Connection": "keep-alive",
    }
    
    if range_header:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        status = 206 # Partial Content
    else:
        status = 200

    response = web.StreamResponse(status=status, headers=headers)
    await response.prepare(request)

    try:
        # Tgcrypto must be installed for maximum speed!
        async for chunk in app.stream_media(message, offset=start):
            await response.write(chunk)
    except Exception as e:
        logger.error(f"Streaming error: {e}")
    
    return response

async def start_services():
    print("----------------------------------------")
    print("Starting Telegram Client...")
    await app.start()

    print("Starting Web Server...")
    web_app = web.Application(client_max_size=0) # No limit on size
    web_app.add_routes(routes)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    me = await app.get_me()
    print(f"DONE! Logged in as: {me.first_name}")
    print(f"WEB SERVER RUNNING ON PORT {PORT}")
    print("----------------------------------------")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Fatal Error: {e}")

