# ---------------------------------------------------------------------------------
                                                      
                                                      
 # _ __ ___   ___  __ _     _ __ ___   ___   __ _ ___  
 #| '_ ` _ \ / _ \/ _` |   | '_ ` _ \ / _ \ / _` / __| 
 #| | | | | |  __/ (_| |   | | | | | | (_) | (_| \__ \ 
 #|_| |_| |_|\___|\__, |   |_| |_| |_|\___/ \__, |___/ 
 #                __/ |_____                __/ |     
  #               |___/______|              |___/      
# Name: QrMod
# Description: create and read qr codes, Interesting 
# Author: @meg_mods
# ---------------------------------------------------------------------------------

# ??    Licensed under the GNU AGPLv3
# ?? https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @meg_mods
# ---------------------------------------------------------------------------------
import io
from PIL import Image
import qrcode
from pyzbar import pyzbar
from telethon.tl.custom import Message
from .. import loader, utils


@loader.tds
class QRMod(loader.Module):
    """Модуль для работы с qr кодами """
    
    strings = {
        "name": "QR",
        "created": "Готово!",
        "no_txt": "нет текста\n<code>{prefix}qr текст</code>",
        "not_found": "qr не найден",
        "result": "результат:\n<code>{text}</code>",
        "wait": "секунду...",
        "no_pic": "нужно фото",
        "err_make": "ошибка: {error}",
        "err_read": "не получилось: {error}",
    }
    
    strings_en = {
        "created": "done ✔️",
        "no_txt": "no text\n<code>{prefix}qr text</code>", 
        "not_found": "qr not found",
        "result": "result:\n<code>{text}</code>",
        "wait": "wait...",
        "no_pic": "need photo",
        "err_make": "error: {error}",
        "err_read": "failed: {error}",
    }

    @loader.command(en_doc="create qr code", ru_doc="создать кьюар код")
    async def qcreate(self, message: Message):
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_txt").format(prefix=self.get_prefix()))
            return

        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=3)
            qr.add_data(args)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)

            await self._client.send_file(message.peer_id, bio, caption=self.strings("created"), reply_to=message.reply_to_msg_id)
            await message.delete()

        except Exception as e:
            await utils.answer(message, self.strings("err_make").format(error=str(e)))

    @loader.command(en_doc="read qr code", ru_doc="просканировать кьюар код")
    async def qread(self, message: Message):
        await utils.answer(message, self.strings("wait"))
        
        photo = None
        if message.media and hasattr(message.media, 'photo'):
            photo = message.media
        elif message.reply_to_msg_id:
            reply = await message.get_reply_message()
            if reply and reply.media and hasattr(reply.media, 'photo'):
                photo = reply.media
        
        if not photo:
            await utils.answer(message, self.strings("no_pic"))
            return

        try:
            photo_bytes = await self._client.download_media(photo, bytes)
            image = Image.open(io.BytesIO(photo_bytes))
            decoded = pyzbar.decode(image)
            
            if not decoded:
                await utils.answer(message, self.strings("not_found"))
                return
            
            data = decoded[0].data.decode('utf-8')
            await utils.answer(message, self.strings("result").format(text=utils.escape_html(data)))

        except Exception as e:
            await utils.answer(message, self.strings("err_read").format(error=str(e)))
