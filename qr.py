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
import logging

from PIL import Image
import qrcode
from pyzbar import pyzbar

from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.markdown import hcode

router = Router()
logger = logging.getLogger(__name__)

# Словарь для хранения строковых ресурсов
STRINGS = {
    "ru": {
        "name": "QR",
        "created": "Готово!",
        "no_txt": "нет текста\n`{prefix}qr текст`",
        "not_found": "qr не найден",
        "result": "результат:\n`{text}`",
        "wait": "секунду...",
        "no_pic": "нужно фото",
        "err_make": "ошибка: {error}",
        "err_read": "не получилось: {error}",
    },
    "en": {
        "created": "done ✔️",
        "no_txt": "no text\n`{prefix}qr text`", 
        "not_found": "qr not found",
        "result": "result:\n`{text}`",
        "wait": "wait...",
        "no_pic": "need photo",
        "err_make": "error: {error}",
        "err_read": "failed: {error}",
    }
}

# Функция-помощник для получения строк в зависимости от языка
def get_string(lang_code: str, key: str) -> str:
    lang = "ru" if lang_code.startswith("ru") else "en"
    return STRINGS.get(lang, STRINGS["ru"]).get(key, "")

# Команды для вашего бота
@router.message(Command("qcreate", "qrc"))
async def qcreate_handler(message: types.Message, bot: Bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        prefix = message.text[0]  # Предполагаем, что префикс - это первый символ команды
        await message.answer(get_string(message.from_user.language_code, "no_txt").format(prefix=prefix), parse_mode=ParseMode.MARKDOWN_V2)
        return

    text_to_encode = args[1]
    
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=3)
        qr.add_data(text_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        
        await message.answer_photo(
            photo=types.BufferedInputFile(bio.getvalue(), filename="qr_code.png"),
            caption=get_string(message.from_user.language_code, "created")
        )

        await message.delete()

    except Exception as e:
        logger.error("Error creating QR code: %s", e)
        await message.answer(get_string(message.from_user.language_code, "err_make").format(error=str(e)))


@router.message(Command("qread", "scan"))
async def qread_handler(message: types.Message, bot: Bot):
    await message.answer(get_string(message.from_user.language_code, "wait"))
    
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif message.reply_to_message and message.reply_to_message.photo:
        photo_file_id = message.reply_to_message.photo[-1].file_id
    
    if not photo_file_id:
        await message.answer(get_string(message.from_user.language_code, "no_pic"))
        return

    try:
        file = await bot.get_file(photo_file_id)
        photo_bytes = await bot.download_file(file.file_path)
        image = Image.open(io.BytesIO(photo_bytes.read()))
        decoded = pyzbar.decode(image)
        
        if not decoded:
            await message.answer(get_string(message.from_user.language_code, "not_found"))
            return
        
        data = decoded[0].data.decode('utf-8')
        await message.answer(
            get_string(message.from_user.language_code, "result").format(text=data),
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        logger.error("Error reading QR code: %s", e)
        await message.answer(get_string(message.from_user.language_code, "err_read").format(error=str(e))) #aiogram3based
