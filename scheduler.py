import asyncio
import aiogram.utils.exceptions
import decouple

from datetime import datetime, timedelta
from binance.actions import get_balance_j2m
from database import balance, binance_db, users, referral, stabpool
from aiogram import Bot, types


async def count_users_profit_collective():
    tg_ids = await users.get_all_tg_id()
    now = datetime.now().date() - timedelta(days=1)
    profit_percentage = await binance_db.get_weekly_profit(now)
    for tg_id in tg_ids:
        deposit = await balance.get_balance_status(tg_id)
        weekly_profit = 0
        try:
            deposit_ = deposit[2]
        except TypeError:
            deposit_ = 0
        if deposit_ < 75000:
            if deposit_ == 0:
                pass
            elif deposit_ < 5000:
                weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.4
            elif 5000 <= deposit_ < 15000:
                weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.45
            elif deposit_ >= 15000:
                weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.5
            await balance.add_weekly_profit(weekly_profit, tg_id)
            line_3 = await referral.get_inviter_id_line3(tg_id)
            line_2 = await referral.get_inviter_id_line2(tg_id)
            line_1 = await referral.get_inviter_id_line1(tg_id)
            referral_percentage = deposit_ * (profit_percentage[0] / 100)
            try:
                if line_1[0]:
                    referral_profit_1 = round(referral_percentage * 0.05, 2)
                    await balance.update_referral_profit(line_1[0], referral_profit_1)
            except TypeError:
                pass
            try:
                if line_2[0]:
                    deposit_line2 = await balance.get_balance_status(line_2[0])
                    try:
                        deposit_line2 = deposit_line2[2]
                    except TypeError:
                        deposit_line2 = 0
                    if deposit_line2 >= 500:
                        referral_profit_2 = round(referral_percentage * 0.03, 2)
                        await balance.update_referral_profit(line_2[0], referral_profit_2)
            except TypeError:
                pass
            try:
                if line_3[0]:
                    deposit_line3 = await balance.get_balance_status(line_3[0])
                    try:
                        deposit_line3 = deposit_line3[2]
                    except TypeError:
                        deposit_line3 = 0
                    if deposit_line3 >= 1000:
                        referral_profit_3 = round(referral_percentage * 0.02, 2)
                        await balance.update_referral_profit(line_3[0], referral_profit_3)
            except TypeError:
                pass


async def count_users_profit_stabpool():
    tg_ids = await users.get_all_tg_id()
    now = datetime.now().date() - timedelta(days=1)
    profit_percentage = await binance_db.get_weekly_profit(now)
    for tg_id in tg_ids:
        deposit = await stabpool.get_balance_status(tg_id)
        try:
            deposit_ = deposit[2]
        except TypeError:
            deposit_ = 0
        weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.6
        await stabpool.add_weekly_profit(weekly_profit, tg_id)
        bot = Bot(token=decouple.config("BOT_TOKEN"))
        session = await bot.get_session()
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=f"<b>📨 [Стабилизационный пул] Отчет на {datetime.now().date().strftime('%d.%m.%Y')}</b>"
                     f"\n\n<em>💰 Ваша доходность за торговую неделю:"
                     f"</em> {round(weekly_profit, 2)} USDT"
                     f"<em>\n\n📈 Общий профит J2M:</em> {round(profit_percentage[0], 2)} %"
                     f"\n\n\n<em>Баланс будет обновлен в течение суток!"
                     f"Возможны незначительные отличия партнерских начислений в отчете от реальных (в пределах 1%)</em>"
                     f"\n\n<a href='https://telegra.ph/Kak-vyschityvaetsya-dohodnost-polzovatelya-J2M-07-21-2'>"
                     f"Подробнее о правилах начисления доходности</a>",
                parse_mode=types.ParseMode.HTML)
            await session.close()
        except aiogram.utils.exceptions.BotBlocked:
            await bot.send_message(chat_id=decouple.config("GROUP_ID"),
                                   text=f"Пользователь с ID {tg_id} заблокировал бота!")
            await session.close()


async def send_message_with_profit_collective():
    all_tg_ids = await users.get_all_tg_id()
    for tg_id in all_tg_ids:
        now = datetime.now().date() - timedelta(days=1)
        profit_percentage = await binance_db.get_weekly_profit(now)
        user_data = await balance.get_balance_status(tg_id)
        try:
            weekly_profit = user_data[8] if user_data[8] is not None else 0
        except TypeError:
            weekly_profit = 0
        line_1_ids = await referral.get_line_1(tg_id)
        line_2_ids = await referral.get_line_2(tg_id)
        line_3_ids = await referral.get_line_3(tg_id)
        referral_profit_line1 = 0
        referral_profit_line2 = 0
        referral_profit_line3 = 0
        ref_x = 0
        ref_x2 = 0
        ref_x3 = 0
        if line_1_ids:
            for line_1_id in line_1_ids[1]:
                referral_profit_line1_data = await balance.get_balance_status(line_1_id)
                if referral_profit_line1_data is not None:
                    count = 0.45
                    ref_x += referral_profit_line1_data[2]
                    if referral_profit_line1_data[2] < 5000:
                        count = 0.4
                    if referral_profit_line1_data[2] > 15000:
                        count = 0.5
                    try:
                        referral_profit_line1 += float(referral_profit_line1_data[8] / count) * 0.05 if referral_profit_line1_data is not None else 0
                    except TypeError:
                        referral_profit_line1 += 0
        if line_2_ids:
            if user_data[2] >= 500:
                for line_2_id in line_2_ids[1]:
                    referral_profit_line2_data = await balance.get_balance_status(line_2_id)
                    if referral_profit_line2_data is not None:
                        count = 0.45
                        ref_x2 += referral_profit_line2_data[2]
                        if referral_profit_line2_data[2] < 5000:
                            count = 0.4
                        if referral_profit_line2_data[2] > 15000:
                            count = 0.5
                        try:
                            referral_profit_line2 += float(referral_profit_line2_data[8] / count) * 0.03 if referral_profit_line2_data is not None else 0
                        except TypeError:
                            referral_profit_line2 += 0
            else:
                referral_profit_line2 = 0
        if line_3_ids:
            if user_data[2] >= 1000:
                for line_3_id in line_3_ids[1]:
                    referral_profit_line3_data = await balance.get_balance_status(line_3_id)
                    if referral_profit_line3_data is not None:
                        ref_x3 += referral_profit_line3_data[2]
                        count = 0.45
                        if referral_profit_line3_data[2] < 5000:
                            count = 0.4
                        if referral_profit_line3_data[2] > 15000:
                            count = 0.5
                        try:
                            referral_profit_line3 += (referral_profit_line3_data[8] / count) * 0.02 if referral_profit_line3_data is not None else 0
                        except TypeError:
                            referral_profit_line3 += 0
            else:
                referral_profit_line3 = 0
        bot = Bot(token=decouple.config("BOT_TOKEN"))
        session = await bot.get_session()
        try:
            if weekly_profit > 0 or referral_profit_line1 > 0 or referral_profit_line2 > 0 or referral_profit_line3 > 0:
                dop = 63.2
                if tg_id == 340862178:
                    dop = 66.21
                print(f"{tg_id} - WP: {weekly_profit} - 1 {referral_profit_line1}, 2 {referral_profit_line2}, 3 {referral_profit_line3} -- !{ref_x + ref_x2 + ref_x3} ")
                try:
                    if tg_id in [340862178, 452517420]:
                        await bot.send_message(
                            chat_id=tg_id,
                            text=f"<b>📨 [Коллективный аккаунт] Отчет на {datetime.now().date().strftime('%d.%m.%Y')}</b>"
                                 f"\n\n<em>💰 Ваша доходность за торговую неделю:"
                                 f"</em> {round(weekly_profit, 2)} USDT"
                                 f"<em>\n\n📈 Общий профит J2M:</em> {round(profit_percentage[0], 2)} %"
                                 f"\n\n<em>👨‍👦‍👦 Партнерские начисления:</em>"
                                 f"\n   ↳ <em>1 линия (5% от дохода): {round(referral_profit_line1, 2)} USDT </em>"
                                 f"\n   ↳ <em>2 линия (3% от дохода): {round(referral_profit_line2, 2)} USDT </em>"
                                 f"\n   ↳ <em>3 линия (2% от дохода): {round(referral_profit_line3, 2)} USDT </em>"
                                 f"\n   ↳ <em> Общие партнерские начисления: "
                                 f"{round(referral_profit_line1 + referral_profit_line2 + referral_profit_line3, 2)} USDT</em>"
                                 f"\n\n<em>Дополнительные начисления J2M:</em> {dop} USDT "
                                 f"\n\n\n<em>Баланс будет обновлен в течение суток!"
                                 f"Возможны незначительные отличия партнерских начислений в отчете от реальных (в пределах 1%)</em>"
                                 f"\n\n<a href='https://telegra.ph/Kak-vyschityvaetsya-dohodnost-polzovatelya-J2M-07-21-2'>"
                                 f"Подробнее о правилах начисления доходности</a>",
                            parse_mode=types.ParseMode.HTML)
                        await session.close()
                    else:
                        await bot.send_message(
                            chat_id=tg_id,
                            text=f"<b>📨 Отчет на {datetime.now().date().strftime('%d.%m.%Y')}</b>"
                                 f"\n\n<em>💰 Ваша доходность за торговую неделю:"
                                 f"</em> {round(weekly_profit, 2)} USDT"
                                 f"<em>\n\n📈 Общий профит J2M:</em> {round(profit_percentage[0], 2)} %"
                                 f"\n\n<em>👨‍👦‍👦 Партнерские начисления:</em>"
                                 f"\n   ↳ <em>1 линия (5% от дохода): {round(referral_profit_line1, 2)} USDT </em>"
                                 f"\n   ↳ <em>2 линия (3% от дохода): {round(referral_profit_line2, 2)} USDT </em>"
                                 f"\n   ↳ <em>3 линия (2% от дохода): {round(referral_profit_line3, 2)} USDT </em>"
                                 f"\n   ↳ <em> Общие партнерские начисления: "
                                 f"{round(referral_profit_line1 + referral_profit_line2 + referral_profit_line3, 2)} USDT</em>"
                                 f"\n\n\n<em>Баланс будет обновлен в течение суток!"
                                 f"Возможны незначительные отличия партнерских начислений в отчете от реальных (в пределах 1%)</em>"
                                 f"\n\n<a href='https://telegra.ph/Kak-vyschityvaetsya-dohodnost-polzovatelya-J2M-07-21-2'>"
                                 f"Подробнее о правилах начисления доходности</a>",
                            parse_mode=types.ParseMode.HTML)
                        await session.close()
                except:
                    await session.close()

            else:
                await bot.send_message(
                    chat_id=tg_id,
                    text=f"<b>📨 Отчет на {datetime.now().date().strftime('%d.%m.%Y')}</b>"
                         f"\n\n<em>💰 Ваша доходность за торговую неделю:"
                         f"</em> Вы не участвовали в торговой неделе. Измените процент реинвестирования и/или пополните баланс!"
                         f"<em>\n\n📈 Общий профит J2M:</em> {round(profit_percentage[0], 2)} %"
                         f"\n\n\n<em>Баланс будет обновлен в течение суток!</em>"
                         f"\n\n<a href='https://telegra.ph/Kak-vyschityvaetsya-dohodnost-polzovatelya-J2M-07-21-2'>"
                         f"Подробнее о правилах начисления доходности</a>",
                    parse_mode=types.ParseMode.HTML)
                await session.close()
        except aiogram.utils.exceptions.BotBlocked:
            await bot.send_message(chat_id=decouple.config("GROUP_ID"),
                                   text=f"Пользователь с ID {tg_id} заблокировал бота!")
            await session.close()


async def weekly_deposit_update():
    tg_ids = await users.get_all_tg_id()
    for tg_id in tg_ids:
        try:
            weekly_deposit = await balance.get_balance_status(tg_id)
            weekly_deposit_stabpool = await stabpool.get_balance_status(tg_id)
            if weekly_deposit[8] != 0 and weekly_deposit[4] == 0:
                await balance.update_weekly_deposit(tg_id, round(weekly_deposit[8], 2))
            if weekly_deposit_stabpool[5] != 0:
                await stabpool.update_weekly_deposit(tg_id, round(weekly_deposit_stabpool[8], 2))
        except TypeError:
            pass


# Баланс J2M
async def scheduler_balance_j2m():
    print(f"Balance J2M start - [{datetime.now()}]")
    while True:
        now = datetime.now()
        user_balance = await get_balance_j2m()
        if now.hour == 12 and now.minute == 34:
            await binance_db.insert_balance_everyday(user_balance[0], user_balance[1])
            print(f"Insert everyday balance at {now.date()}")
        if now.weekday() == 0 and now.hour == 15 and now.minute == 0:
            await binance_db.insert_balance_j2m_monday(user_balance[0], user_balance[1])
            print(f"Insert monday balance at {now.date()}")
        if now.weekday() == 6 and now.hour == 16 and now.minute == 0:
            await binance_db.insert_balance_j2m_sunday(user_balance[0], user_balance[1])
            print(f"Insert sunday balance at {now.date()}")
        await asyncio.sleep(60 - now.second)


# Понедельник
async def balance_to_deposit():
    print(f"Balance to deposit start - [{datetime.now()}]")
    while True:
        now = datetime.now()
        if now.weekday() == 0 and now.hour == 17 and now.minute == 0:
            await weekly_deposit_update()
            print(f"Update deposit with weekly profit for all users at {now.date()}")
        if now.weekday() == 0 and now.hour == 20 and now.minute == 0:
            await balance.balance_to_deposit_autoreinvest()
            print(f"Update balance to deposit on auto-reinvest users at {now.date()}")
            await balance.balance_to_deposit_invest()
            print(f"Update balance to deposit on invest users at {now.date()}")
        await asyncio.sleep(60 - now.second)


# Воскресенье
async def deposit_to_balance():
    print(f"Scheduler run at {datetime.now()}")
    while True:
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
            await count_users_profit_collective()
        if now.weekday() == 6 and now.hour == 20 and now.minute == 0:
            await balance.transfer_deposit_to_balance()
        await asyncio.sleep(60 - now.second)

# async def main():
#     loop = asyncio.get_running_loop()
#     tasks = [
#         loop.create_task(scheduler_balance_j2m()),
#         loop.create_task(balance_to_deposit()),
#         loop.create_task(deposit_to_balance())
#     ]
#     await asyncio.gather(*tasks)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
