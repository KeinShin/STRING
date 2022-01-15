#    Copyright 2021 Toxic
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import asyncio
from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from pyrogram.errors import (
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyromod import listen

bot = Client(
    "ses bot",
    os.environ.get("TG_APP_ID"),
    os.environ.get("TG_API_HASH"),
    bot_token = os.environ.get("TOKEN")
)


@bot.on_message(filters.command("string") & filters.user(OWNER) & filters.private)
async def stringsessiongenerator(client, message):
    chat = message.chat
    while True:
        number = await bot.ask(
            chat.id,
            "Please Send Your Phone Number in International Format.\n**Example: +91xxxxxxxxxxx**",
        )
        if not number.text:
            continue
        phone = number.text.strip()
        if phone.startswith("/"):
            continue
        confirm = await bot.ask(
            chat.id,
            f'`Is "{phone}" correct?` \n\nSend: `y` if correct\nSend: `n` if incorrect',
        )
        if confirm.text.startswith("/"):
            continue
        if "y" in confirm.text.lower():
            break
    try:
        temp_client = Client(
            ":memory:",
            api_id=6,
            api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
        )
    except Exception as e:
        await bot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        return
    try:
        await temp_client.connect()
    except ConnectionError:
        await temp_client.disconnect()
        await temp_client.connect()
    try:
        code = await temp_client.send_code(phone)
        await asyncio.sleep(2)
    except PhoneNumberInvalid:
        await message.reply_text("Phone Number is Invalid :(")
        return
    try:
        otp = await bot.ask(
            chat.id,
            (
                "An OTP is sent to your phone number, "
                "Please enter OTP in `1 2 3 4 5` format. __(Space between each number!)__"
            ),
            timeout=300,
        )
    except TimeoutError:
        await message.reply_text(
            "Time limitation reached of 5 min. Process Cancelled...",
        )
        return
    otp_code = otp.text
    try:
        await temp_client.sign_in(
            phone,
            code.phone_code_hash,
            phone_code=" ".join(str(otp_code)),
        )
    except PhoneCodeInvalid:
        await message.reply_text("Invalid OTP :(")
        return
    except PhoneCodeExpired:
        await message.reply_text("OTP is Expired :(")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id,
                "Your account has Two-Step Verification.\nPlease enter your Password.",
                timeout=300,
            )
        except TimeoutError:
            await message.reply_text("Time limitation reached of 5 min :(")
            return
        new_code = two_step_code.text
        try:
            await temp_client.check_password(new_code)
        except Exception as e:
            await message.reply_text(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await temp_client.export_session_string()
        await temp_client.disconnect()
        await bot.send_message(
            chat.id,
            text=f"**HERE IS YOUR STRING SESSION:**\n```{session_string}```\n\n**âš ï¸ Warning : Don't share your string session with anyone. They can easily access to your account via it!**",
        )
    except Exception as e:
        await bot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        return

    
  bot.run()
