import asyncio
from datetime import datetime, timedelta
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# Логтарды баптау
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------
# БОТ БАПТАУЛАРЫ
# -------------------------------------------------------------
API_TOKEN = "8639374056:AAH9ZMSGiHvax9EwFm2zQMnh2akmIIKNwjo"
ADMIN_ID = 1901471929
CHANNEL_ID = -1004308911511

KASPI_NUMBER = "+7 708 508 51 85"
KASPI_NAME = "Қазыбек И."
ADMIN_USERNAME = "@QazekeIssa"
CHANNEL_LINK = "https://t.me/+GiV00YidR7xmMWQy"  # Ссылка на ваш закрытый канал

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------------------------------------------------
# ДЕРЕКТЕР БАЗАСЫН БАПТАУ (SQLite)
# -------------------------------------------------------------


def init_db():
  conn = sqlite3.connect("subscriptions.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            end_date TEXT
        )
    """)
  conn.commit()
  conn.close()


def add_or_update_sub(user_id: int, days: int):
  conn = sqlite3.connect("subscriptions.db")
  cursor = conn.cursor()
  cursor.execute("SELECT end_date FROM users WHERE user_id = ?", (user_id,))
  row = cursor.fetchone()

  now = datetime.now()
  if row:
    current_end = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    if current_end > now:
      new_end = current_end + timedelta(days=days)
    else:
      new_end = now + timedelta(days=days)
  else:
    new_end = now + timedelta(days=days)

  formatted_end = new_end.strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      "INSERT OR REPLACE INTO users (user_id, end_date) VALUES (?, ?)",
      (user_id, formatted_end),
  )
  conn.commit()
  conn.close()
  return new_end


def get_sub_end(user_id: int):
  conn = sqlite3.connect("subscriptions.db")
  cursor = conn.cursor()
  cursor.execute("SELECT end_date FROM users WHERE user_id = ?", (user_id,))
  row = cursor.fetchone()
  conn.close()
  if row:
    return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
  return None


def remove_sub(user_id: int):
  conn = sqlite3.connect("subscriptions.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
  conn.commit()
  conn.close()


# -------------------------------------------------------------
# МЕНЮЛЕР
# -------------------------------------------------------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Жазылым алу (Тарифтер)")],
        [
            KeyboardButton(text="🎬 Фильмдер каталогы"),
            KeyboardButton(text="👤 Менің профилім"),
        ],
        [
            KeyboardButton(text="📝 Өтінім қалдыру"),
            KeyboardButton(text="👨‍💻 Қолдау көрсету"),
        ],
    ],
    resize_keyboard=True,
)

tariff_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚡️ 1 апта — 700 тг", callback_data="tariff_1week"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏳ 2 апта — 1000 тг", callback_data="tariff_2weeks"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗓 1 ай — 1500 тг", callback_data="tariff_1month"
            )
        ],
    ]
)

# -------------------------------------------------------------
# ХЕНДЛЕРЛЕР
# -------------------------------------------------------------


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
  welcome_text = (
      f"Сәлем! 👋🍿\n\n"
      f"🎬 QAZFilms ботына қош келдіңіз! ✨\n"
      f"Бұл жерден ең үздік фильмдер мен сериалдарды тамашалай аласыз. 🎥🔥\n\n"
      f"👇 Қызметті пайдалану үшін төмендегі менюден керекті бөлімді"
      f" таңдаңыз:"
  )
  await message.answer(welcome_text, reply_markup=main_menu, parse_mode="Markdown")


@dp.message(F.text == "💳 Жазылым алу (Тарифтер)")
async def show_tariffs(message: types.Message):
  await message.answer(
      "✨ **Өзіңізге ыңғайлы тарифті таңдаңыз:**\n\n"
      "• ⚡️ 1 апталық доступ — **700 тг**\n"
      "• ⏳ 2 апталық доступ — **1000 тг**\n"
      "• 🗓 1 айлық доступ — **1500 тг**",
      reply_markup=tariff_menu,
      parse_mode="Markdown",
  )


@dp.callback_query(
    F.data.in_({"tariff_1week", "tariff_2weeks", "tariff_1month"})
)
async def process_tariff(callback_query: types.CallbackQuery):
  if callback_query.data == "tariff_1week":
    tariff_name = "1 апта (700 тг)"
  elif callback_query.data == "tariff_2weeks":
    tariff_name = "2 апта (1000 тг)"
  else:
    tariff_name = "1 ай (1500 тг)"

  pay_text = (
      f"✅ **Таңдалған тариф:** {tariff_name}\n\n"
      f"📲 **Төлем жасау реквизиттері:**\n"
      f"• **Kaspi:** `{KASPI_NUMBER}`\n"
      f"• **Алушы:** {KASPI_NAME}\n\n"
      f"⚠️ **Маңызды:** Төлем жасаған соң, чекті осы чатқа жіберіңіз немесе"
      f" тікелей админге жазыңыз: {ADMIN_USERNAME}"
  )
  await callback_query.answer()
  await bot.send_message(
      callback_query.from_user.id, pay_text, parse_mode="Markdown"
  )


@dp.message(F.text == "🎬 Фильмдер каталогы")
async def show_catalog(message: types.Message):
  await message.answer(
      "🍿 **Фильмдер каталогы:**\n\n"
      "Жабық каналға өту және барлық фильмдерді көру үшін жазылымыңыз белсенді"
      " болуы керек.\nЖазылым алу үшін «💳 Жазылым алу (Тарифтер)» бөлімін"
      " таңдаңыз.",
      parse_mode="Markdown",
  )


@dp.message(F.text == "👤 Менің профилім")
async def show_profile(message: types.Message):
  user_id = message.from_user.id
  now = datetime.now()
  end_date = get_sub_end(user_id)

  if end_date and end_date > now:
    sub_end_date = end_date.strftime("%d.%m.%Y %H:%M")
    status_text = f"Белсенді 🟢\n• Аяқталу мерзімі: **{sub_end_date}**"
  else:
    status_text = "Жазылым жоқ 🔐"

  profile_text = (
      f"👤 **Жеке кабинет**\n\n"
      f"• Аты-жөні: {message.from_user.full_name}\n"
      f"• Telegram ID: `{user_id}`\n"
      f"• Мәртебесі: {status_text}\n\n"
      f"💡 *Төлем жасаған соң, чекті чатқа жіберсеңіз, админ жабық каналға"
      f" сілтеме береді.*"
  )
  await message.answer(profile_text, parse_mode="Markdown")


@dp.message(F.text == "📝 Өтінім қалдыру")
async def request_sub(message: types.Message):
  await message.answer(
      f"🧾 Төлем чегін (скриншот) осы чатқа жіберіңіз немесе тікелей админге"
      f" жазыңыз:\n👉 {ADMIN_USERNAME}"
  )


@dp.message(F.text == "👨‍💻 Қолдау көрсету")
async def support(message: types.Message):
  await message.answer(
      f"💬 Қандай да бір сұрақтарыңыз немесе мәселелеріңіз болса, әкімшіге"
      f" жазыңыз:\n👉 {ADMIN_USERNAME}"
  )


# -------------------------------------------------------------
# ЧЕК ТҮСКЕНДЕ АДМИНГЕ ХАБАРЛАМА ЖІБЕРУ
# -------------------------------------------------------------
@dp.message(F.photo | F.document)
async def process_receipt(message: types.Message):
  user_id = message.from_user.id

  admin_markup = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⚡️ 1 апта қосу", callback_data=f"sub_7_{user_id}"
              ),
              InlineKeyboardButton(
                  text="⏳ 2 апта қосу", callback_data=f"sub_14_{user_id}"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="🗓 1 ай қосу", callback_data=f"sub_30_{user_id}"
              )
          ],
          [
              InlineKeyboardButton(
                  text="❌ Қабылдамау", callback_data=f"reject_{user_id}"
              )
          ],
      ]
  )

  admin_notification = (
      f"📩 **Жаңа төлем чегі!**\n\n"
      f"👤 Жіберуші: {message.from_user.full_name}"
      f" (@{message.from_user.username})\n"
      f"🆔 ID: `{user_id}`\n\n"
      f"👇 **Жазылым мерзімін таңдаңыз:**"
  )

  await message.answer(
      "✅ Чек қабылданды! Админ тексеріп, жақын арада жабық каналға сілтеме"
      " жібереді."
  )
  await bot.send_message(
      ADMIN_ID,
      admin_notification,
      reply_markup=admin_markup,
      parse_mode="Markdown",
  )
  await message.forward(ADMIN_ID)


@dp.callback_query(F.data.startswith("sub_"))
async def approve_subscription(callback: types.CallbackQuery):
  data_parts = callback.data.split("_")
  days = int(data_parts[1])
  user_id = int(data_parts[2])

  end_date = add_or_update_sub(user_id, days)
  formatted_date = end_date.strftime("%d.%m.%Y")

  success_text = (
      f"🎉 **Төлеміңіз расталды!**\n\n"
      f"✅ Жазылым мерзімі: **{formatted_date}** дейін белсендірілді.\n\n"
      f"Жабық каналға өту үшін төмендегі сілтемені басыңыз:\n"
      f"👉 {CHANNEL_LINK}"
  )
  try:
    await bot.send_message(user_id, success_text, parse_mode="Markdown")
    await callback.message.edit_text(
        callback.message.text
        + f"\n\n✅ ҚАБЫЛДАНДЫ! ({days} күн берілді. {formatted_date} дейін"
        f" сақталды)"
    )
  except Exception as e:
    await callback.answer("Қателік: Пайдаланушыға хабарлама жіберілмеді.")


@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: types.CallbackQuery):
  user_id = int(callback.data.split("_")[1])

  reject_text = (
      f"❌ **Төлеміңіз расталмады.**\n\n"
      f"Чек дұрыс емес немесе төлем түспеген. Сұрақтарыңыз болса админге"
      f" жазыңыз: {ADMIN_USERNAME}"
  )
  try:
    await bot.send_message(user_id, reject_text, parse_mode="Markdown")
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ **ӨТІНІМ ҚАБЫЛДАНМАДЫ.**"
    )
  except Exception as e:
    await callback.answer("Қателік: Пайдаланушыға хабарлама жіберілмеді.")


# -------------------------------------------------------------
# АВТО-КИК ФУНКЦИЯСЫ
# -------------------------------------------------------------
async def auto_kick_expired_users():
  while True:
    try:
      conn = sqlite3.connect("subscriptions.db")
      cursor = conn.cursor()
      now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      cursor.execute(
          "SELECT user_id FROM users WHERE end_date < ?", (now_str,)
      )
      expired_users = cursor.fetchall()
      conn.close()

      for (u_id,) in expired_users:
        try:
          await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=u_id)
          await bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=u_id)
          remove_sub(u_id)

          await bot.send_message(
              u_id,
              "⏳ **Сіздің жазылым мерзіміңіз аяқталды.**\n\n"
              "Каналға қайта кіру үшін жазылымды ұзартыңыз: /start",
              parse_mode="Markdown",
          )
        except Exception as e:
          remove_sub(u_id)

    except Exception as e:
      logging.error(f"Авто-кик қатесі: {e}")

    await asyncio.sleep(3600)


# -------------------------------------------------------------
# БОТТЫ ІСКЕ ҚОСУ
# -------------------------------------------------------------
async def main():
  init_db()
  asyncio.create_task(auto_kick_expired_users())
  await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
  asyncio.run(main())
