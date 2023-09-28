from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.thedex_db import get_transaction


async def main_menu(lang, tg_id) -> InlineKeyboardMarkup:
    trans = await get_transaction(tg_id)
    if not trans:
        balance, refill, withdrawal, structure, support, information = ["Баланс", "⬆️ Пополнение", "Вывод",
                                                                        "Партнерская программа", "Поддержка",
                                                                        "Информация"]
        if lang == "EN":
            balance, refill, withdrawal, structure, support, information = ["Balance", "⬆️ Refill", "Withdrawal",
                                                                            "Affiliate program", "Support",
                                                                            "Information"]
    else:
        balance, refill, withdrawal, structure, support, information = ["Баланс", "‼️ НЕЗАКОНЧЕННАЯ ТРАНЗАКЦИЯ",
                                                                        "Вывод",
                                                                        "Партнерская программа", "Поддержка",
                                                                        "Информация"]
        if lang == "EN":
            balance, refill, withdrawal, structure, support, information = ["Balance", "‼️ UNCOMPLETED TRANSACTION",
                                                                            "Withdrawal", "Partner Program", "Support",
                                                                            "Information"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'💵 {balance}', callback_data='balance')],
        [InlineKeyboardButton(f'🪪 {structure}', callback_data='structure')],
        [InlineKeyboardButton(f' {refill}', callback_data='refill')],
        [InlineKeyboardButton(f'⬇️ {withdrawal}', callback_data='withdrawal')],
        [InlineKeyboardButton(f'🧑‍💻 {support}', callback_data='support'),
         InlineKeyboardButton(f'📒 {information}', callback_data='information')],
        [InlineKeyboardButton(f'🤖 J2MGPT BETA', url='https://t.me/j2m_gptbot')]
    ])
    return kb


def main_menu_short(lang) -> InlineKeyboardMarkup:
    balance, support, information = ["Кошелек", "Поддержка", "Информация"]
    if lang == "EN":
        balance, support, information = ["Wallet", "Support", "Information"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'💵 {balance}', callback_data='balance')],
        [InlineKeyboardButton(f'🧑‍💻 {support}', callback_data='support_short'),
         InlineKeyboardButton(f'📒 {information}', callback_data='information')]
    ])
    return kb


def back_button(lang) -> InlineKeyboardMarkup:
    button = 'Главное меню'
    if lang == "EN":
        button = "Main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'◀️ {button}', callback_data='main_menu')]
    ])
    return kb


def back_menu(lang) -> InlineKeyboardMarkup:
    button = 'Назад'
    if lang == "EN":
        button = "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'◀️ {button}', callback_data='back')]
    ])
    return kb


def language() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🇷🇺 Русский', callback_data='ru'),
         InlineKeyboardButton('🇺🇸 English', callback_data='en')]
    ])
    return kb


def balance_history(lang) -> InlineKeyboardMarkup:
    refill_history, withdrawal_history, back = ["История пополнений", "История выводов", "Главное меню"]
    if lang == "EN":
        refill_history, withdrawal_history, back = ["Refill history", "Withdrawal history", "Main menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'⬆️ {refill_history}', callback_data='refill_history'),
         InlineKeyboardButton(f'⬇️ {withdrawal_history}', callback_data='withdrawal_history')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='main_menu')]
    ])
    return kb


def user_terms(lang) -> InlineKeyboardMarkup:
    text = "Принимаю"
    if lang == "EN":
        text = "Accept"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{text}", callback_data='terms_accept')]
    ])
    return kb


def user_terms_2(lang) -> InlineKeyboardMarkup:
    text, text2 = ["Принимаю", "Подтвердить"]
    if lang == "EN":
        text, text2 = ["Accept", "Confirm"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {text}", callback_data='terms_accept')],
        [InlineKeyboardButton(f"{text2}", callback_data="terms_done")]
    ])
    return kb


def user_docs(lang) -> InlineKeyboardMarkup:
    text = "Принимаю"
    if lang == "EN":
        text = "Accept"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{text}", callback_data='docs_accept')]
    ])
    return kb


def user_docs_2(lang) -> InlineKeyboardMarkup:
    text, text2 = ["Принимаю", "Подтвердить"]
    if lang == "EN":
        text, text2 = ["Accept", "Confirm"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {text}", callback_data='docs_accept')],
        [InlineKeyboardButton(f"{text2}", callback_data="docs_done")]
    ])
    return kb


def referral_statistic(lang) -> InlineKeyboardMarkup:
    text, data, back = 'Подробная статистика', "Личные данные", "Главное меню"
    if lang == "EN":
        text, data, back = "Detailed statistic", "Personal data", "Main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📊 {text}", callback_data='full_statistic')],
        [InlineKeyboardButton(f"🧘 {data}", callback_data="user_data")],
        [InlineKeyboardButton(f"◀️ {back}", callback_data="main_menu")]
    ])
    return kb


def referral_lines(lang) -> InlineKeyboardMarkup:
    text1, text2, text3, back = "1 линия", "2 линия", "3 линия", "Вернуться назад"
    if lang == "EN":
        text1, text2, text3, back = "Line 1", "Line 2", "Line3", "Go Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🧍‍♂️ {text1}", callback_data='line1'),
         InlineKeyboardButton(f"👬 {text2}", callback_data='line2'),
         InlineKeyboardButton(f"👨‍👨‍👦 {text3}", callback_data='line3')],
        [InlineKeyboardButton(f"🔙 {back}", callback_data="structure")]
    ])
    return kb


def detailed_statistic(lang) -> InlineKeyboardMarkup:
    back = "Вернуться назад"
    if lang == "EN":
        back = "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🔙 {back}", callback_data="full_statistic")]
    ])
    return kb


def information_back(lang) -> InlineKeyboardMarkup:
    back = "Вернуться назад"
    if lang == "EN":
        back = "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🔙 {back}", callback_data="information")]
    ])
    return kb


def yesno(lang) -> InlineKeyboardMarkup:
    yes_button, no_button = "Да", "Нет"
    if lang == "EN":
        yes_button, no_button = "Yes", "No"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👍 {yes_button}", callback_data="yes"),
         InlineKeyboardButton(f"👎 {no_button}", callback_data="no")]
    ])
    return kb


def yesno_refill(lang) -> InlineKeyboardMarkup:
    yes_button, no_button, skip_button = "Да", "Нет", "Пропустить"
    if lang == "EN":
        yes_button, no_button, skip_button = "Yes", "No", "Skip"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👍 {yes_button}", callback_data="yes"),
         InlineKeyboardButton(f"👎 {no_button}", callback_data="no")],
        [InlineKeyboardButton(f"⏭️ {skip_button}", callback_data="yes")]
    ])
    return kb


def refill_account(lang) -> InlineKeyboardMarkup:
    first_button, second_button, stabpool = "Личный аккаунт от 15 000 USD", "Коллективный аккаунт от 50 USD", \
        "Стабилизационный пул"
    if lang == "EN":
        first_button, second_button = "Personal account starting from 15 000 USDT", \
            "Collective account starting from 500 USDT."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="active_15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="active_500")],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data="stabpool")]
    ])
    return kb


def refill_account_2(lang) -> InlineKeyboardMarkup:
    first_button, second_button, stabpool, back = "Личный аккаунт от 15 000 USD", "Коллективный аккаунт от 50 USDT", \
        "Стабилизационный пул", "Назад"
    if lang == "EN":
        first_button, second_button, stabpool, back = "Personal account starting from 15,000 USD", \
            "Collective account starting from 50 USD.", "Stab Pool", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="500")],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data="stabpool")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='refill')]
    ])
    return kb


def continue_refill(lang) -> InlineKeyboardMarkup:
    button = "Продолжить"
    if lang == "EN":
        button = "Continue"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"⏩ {button}", callback_data="refill")]
    ])
    return kb


def refill_500_choice(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3, back = "от 500 до 1000 USDT", "от 1000 USDT", "Личный аккаунт от 25 000 USDT", "Назад"
    if lang == "EN":
        button, button_2, button_3, back = "from 500 to 1000 USDT", "from 1000 USDT", \
            "Personal account from 15 000 USDT", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💵 {button}", callback_data="from_500")],
        [InlineKeyboardButton(f"💰 {button_2}", callback_data="from_1000")],
        [InlineKeyboardButton(f"💰💰 {button_3}", callback_data="15000")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='deposit_funds')]
    ])
    return kb


def return_currencies() -> InlineKeyboardMarkup:
    crypto_dict = {
        # 'Bitcoin': 'BTC_BITCOIN',
        # 'Ethereum': 'ETH_ETHEREUM',
        'USDT TRC-20': 'USDT_TRON',
        'USDT ERC-20': 'USDT_ETHEREUM',
        # 'Tron': 'TRX_TRON',
        # 'Litecoin': 'LTC_LITECOIN',
        # 'Binance Coin': 'BNB_BSC',
        # 'Binance USD': 'BUSD_BSC'
    }
    kb = InlineKeyboardMarkup()
    for key, value in crypto_dict.items():
        button = InlineKeyboardButton(key, callback_data=value)
        kb.add(button)
    return kb


def finish_transaction(lang) -> InlineKeyboardMarkup:
    button, button2 = "Оплата завершена", "Отмена транзакции"
    if lang == "EN":
        button, button2 = "Payment completed", "Cancel"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {button}", callback_data="finish_payment")],
        [InlineKeyboardButton(f"❌ {button2}", callback_data="cancel_payment")]
    ])
    return kb


def transaction_status(lang) -> InlineKeyboardMarkup:
    button = "Проверить еще раз"
    button_2 = "Детали транзакции"
    button3 = "Отмена транзакции"
    if lang == "EN":
        button = "Please double-check again"
        button_2 = "Transaction Detail"
        button3 = "Cancel"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🔄 {button}", callback_data="transaction_status"),
         InlineKeyboardButton(f"🧩 {button_2}", callback_data="transaction_detail")],
        [InlineKeyboardButton(f"❌ {button3}", callback_data="cancel_payment")]
    ])
    return kb


def withdrawal_confirmation(lang) -> InlineKeyboardMarkup:
    button, button_2 = "Вывести средства", "Отмена операции"
    if lang == "EN":
        button, button_2 = "Withdraw funds", "Cancel operation"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {button}", callback_data="withdrawal_confirmation")],
        [InlineKeyboardButton(f"❌ {button_2}", callback_data="main_menu")]
    ])
    return kb


def finish_withdrawal(lang) -> InlineKeyboardMarkup:
    button, button_2 = "Подтвердить", "Отменить"
    if lang == "EN":
        button, button_2 = "Confirm", "Cancel"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {button}", callback_data="confirm_withdrawal"),
         InlineKeyboardButton(f"❌ {button_2}", callback_data="cancel_withdrawal")]
    ])
    return kb


def hold_kb(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3 = "30 дней", "90 дней", "180 дней"
    if lang == "EN":
        button, button_2, button_3 = "30 days", "60 days", "90 days"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button}", callback_data="30"),
         InlineKeyboardButton(f"{button_2}", callback_data="90"),
         InlineKeyboardButton(f"{button_3}", callback_data="180")]
    ])
    return kb


def main_withdraw(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3, button_4 = "Вывод средств", "Изменить кошелек для вывода", \
        "Изменить процент реинвестирования", "Вернуться в главное меню"
    if lang == "EN":
        button, button_2, button_3, button_4 = "Withdraw funds", "Change wallet", \
            "Change reinvestment percentage", "Back to main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🔽 {button}", callback_data="withdrawal_funds")],
        [InlineKeyboardButton(f"🔀 {button_2}", callback_data="change_wallet")],
        [InlineKeyboardButton(f"🧮 {button_3}", callback_data="change_percentage")],
        [InlineKeyboardButton(f"◀️ {button_4}", callback_data="main_menu")]
    ])
    return kb


def withdraw_percentage(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3 = "Ничего", "50%", "100%"
    if lang == "EN":
        button, button_2, button_3 = "None", "50%", "100%"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button}", callback_data="0"),
         InlineKeyboardButton(f"{button_2}", callback_data="50"),
         InlineKeyboardButton(f"{button_3}", callback_data="100")]
    ])
    return kb


def get_nft(lang) -> InlineKeyboardMarkup:
    button, support = "Приобрести NFT", "Связаться с поддержкой"
    if lang == "EN":
        button, support = "Get NFT", "Connect with support"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button}", callback_data="get_nft")],
        [InlineKeyboardButton(f'🧑‍💻 {support}', callback_data="support_nft")]])
    return kb


def check_nft_status(lang) -> InlineKeyboardMarkup:
    button, button_2 = "Обновить", "Детали транзакции"
    if lang == "EN":
        button, button_2 = "Refresh", "Transaction Details"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button}", callback_data="refresh_nft"),
         InlineKeyboardButton(f"{button_2}", callback_data="transaction_details_nft")]])
    return kb


def refill_main_menu(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3 = "Изучить условия", "Пополнить баланс", "Вернуться в главное меню"
    if lang == "EN":
        button, button_2, button_3 = "To review the terms", "To deposit funds", "Return to main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"‍🎓️ {button}", callback_data="review_terms"),
         InlineKeyboardButton(f"💵 {button_2}", callback_data="deposit_funds")],
        [InlineKeyboardButton(f"◀️ {button_3}", callback_data="main_menu")]
    ])
    return kb


def distribution(lang) -> InlineKeyboardMarkup:
    button, back = "Условия применения ПО", "Назад"
    if lang == "EN":
        button, back = "Terms of software usage", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {button}", callback_data="distribution")],
        [InlineKeyboardButton(f"◀️ {back}", callback_data="refill")]])
    return kb


def active_50(lang) -> InlineKeyboardMarkup:
    partner, button_1, button_2, stabpool, back = "Условия партнерской программы", "Изучить условия от 5000 USDT", \
        "Изучить условия от 15000 USDT", "Стабилизационный пул", "Назад"
    if lang == "EN":
        partner, button_1, button_2, stabpool, back = "Partner Program Terms", "Explore terms from 5000 USDT", \
            "Explore terms from 15000 USDT", "Stabilization Pool", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {partner}", callback_data="partners")],
        [InlineKeyboardButton(f"💵 {button_1}", callback_data="active_5000")],
        [InlineKeyboardButton(f"💵 {button_2}", callback_data="active_15000")],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data='stabpool_terms')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='distribution')]
    ])
    return kb


def active_5000(lang) -> InlineKeyboardMarkup:
    partner, button_1, button_2, stabpool, back = "Условия партнерской программы", "Изучить условия от 50 USDT", \
        "Изучить условия от 15000 USDT", "Стабилизационный пул", "Назад"
    if lang == "EN":
        partner, button_1, button_2, stabpool, back = "Partner Program Terms", "Explore terms from 50 USDT", \
            "Explore terms from 15000 USDT", "Stabilization Pool", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {partner}", callback_data="partners")],
        [InlineKeyboardButton(f"💵 {button_1}", callback_data="active_50")],
        [InlineKeyboardButton(f"💵 {button_2}", callback_data="active_15000")],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data='stabpool_terms')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='distribution')]
    ])
    return kb


def active_15000(lang) -> InlineKeyboardMarkup:
    partner, button_1, button_2, stabpool, back = "Условия партнерской программы", "Изучить условия от 50 USDT", \
        "Изучить условия от 5000 USDT", "Стабилизационный пул", "Назад"
    if lang == "EN":
        partner, button_1, button_2, stabpool, back = "Partner Program Terms", "Explore terms from 5000 USDT", \
            "Explore terms from 15000 USDT", "Stabilization Pool", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {partner}", callback_data="partners")],
        [InlineKeyboardButton(f"💵 {button_1}", callback_data="active_50")],
        [InlineKeyboardButton(f"💵 {button_2}", callback_data="active_5000")],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data='stabpool_terms')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='distribution')]
    ])
    return kb


def stabpool_kb(lang) -> InlineKeyboardMarkup:
    button, button_1, button_2, button_3, back = "Участвовать в стабилизационном пуле", "Изучить условия от 50 USDT", \
        "Изучить условия от 5000 USDT", "Изучить условия от 15000 USDT", "Назад"
    if lang == "EN":
        button, button_1, button_2, button_3, back = "Participate in stabilization pool", \
            "Explore terms from 50 USDT", "Explore terms from 5000 USDT", "Explore terms from 15000 USDT", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {button}", callback_data="stabpool")],
        [InlineKeyboardButton(f"💵 {button_1}", callback_data="active_50")],
        [InlineKeyboardButton(f"💵 {button_2}", callback_data="active_5000")],
        [InlineKeyboardButton(f"💵 {button_3}", callback_data="active_15000")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='distribution')]
    ])
    return kb


def partners_kb(lang) -> InlineKeyboardMarkup:
    button_1, button_2 = "Вернуться к описанию категорий", "Разместить активы"
    if lang == "EN":
        button_1, button_2 = "Return to Category Descriptions", "Place Assets"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {button_1}", callback_data="distribution")],
        [InlineKeyboardButton(f"📖 {button_2}", callback_data="deposit_funds")],
    ])
    return kb


def emailing_documents(lang) -> InlineKeyboardMarkup:
    button = "Документы отправлены"
    if lang == "EN":
        button = "The documents have been sent"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📨 {button}", callback_data="emailing_documents")]])
    return kb


def support_menu(status) -> InlineKeyboardMarkup:
    button_1, button_2, button3 = "Support SONERA", "Support J2M", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button_1}", url="https://t.me/sonera_help")],
        [InlineKeyboardButton(f"{button_2}", url="https://t.me/J2M_Support")],
        [InlineKeyboardButton(f"{button3}", callback_data=status)]
    ])
    return kb


def change_data(lang) -> InlineKeyboardMarkup:
    button_1, button_2, back = "Изменить имя", "Изменить соц.сети", "Вернуться назад"
    if lang == 'EN':
        button_1, button_2, back = "Change name", "Change socials", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🚶 {button_1}", callback_data="change_name")],
        [InlineKeyboardButton(f"🌐 {button_2}", callback_data='change_socials')],
        [InlineKeyboardButton(f"◀️ {back}", callback_data='structure')]
    ])
    return kb


def refill_account_3(lang) -> InlineKeyboardMarkup:
    first_button, second_button, third_button, stabpool, back = "Категория 1 (от 50 USDT до 4999 USDT)", \
        "Категория 2 (от 5000 USDT до 14 999 USDT)", "Категория 3 (от 15000 USDT)", "Стабилизационный пул", "Назад"
    if lang == "EN":
        first_button, second_button, third_button, stabpool, back = "Category 1 (from 50 USDT to 4999 USDT)", \
            "Category 2 (from 5000 USDT to 14,999 USDT)", "Category 3 (from 15000 USDT)", "Stabilization Pool", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="active_50")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="active_5000")],
        [InlineKeyboardButton(f"💵 {third_button}", callback_data='active_15000')],
        [InlineKeyboardButton(f"💵 {stabpool}", callback_data='stabpool_terms')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='review_terms')]
    ])
    return kb


def emailing_alias(lang) -> InlineKeyboardMarkup:
    button = "Информация отправлена"
    if lang == "EN":
        button = "The information have been sent"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📨 {button}", callback_data="emailing_alias")]])
    return kb


def email_verif(lang) -> InlineKeyboardMarkup:
    button_1, button_2 = "Отправить другой код", "Изменить почту"
    if lang == "EN":
        button_1, button_2 = "Send another code", "Change email"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📨 {button_1}", callback_data="new_code")],
        [InlineKeyboardButton(f"📧 {button_2}", callback_data="change_email")]
    ])
    return kb


def tax_fee() -> InlineKeyboardMarkup:
    button = "Оплатить"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💸 {button}", callback_data="tax_fee")]])
    return kb


def withdrawal_account(lang) -> InlineKeyboardMarkup:
    first_button, second_button, third_button, back = "Вывод с личного аккаунта (от 15 000 USDT)", \
        "Вывод с коллективного аккаунта (от 500 USDT)", "Вывод со стабилизационного пула", "Назад"
    if lang == "EN":
        first_button, second_button, third_button, back = "Withdrawal from personal account (starting from 15,000 USDT)", \
            "Withdrawal from collective account (starting from 500 USDT)", "Withdraw from stabilization pool", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="withdrawal_15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="withdrawal_500")],
        [InlineKeyboardButton(f"💲 {third_button}", callback_data="withdrawal_stabpool")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='withdrawal')]
    ])
    return kb


def information_menu(lang) -> InlineKeyboardMarkup:
    dao, documents, products, collaboration, news, marketing, back = [
        "О DAO J2M", "Документы", "Продукты",
        "Сотрудничество", "Новости", "Маркетинг", "Главное меню"]
    if lang == "EN":
        dao, documents, products, collaboration, news, marketing, back = [
            "About DAO J2M", "Documents", "Products",
            "Collaboration", "News", "Marketing", "Main Menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{dao}", callback_data="dao"),
         InlineKeyboardButton(f"{documents}", callback_data="info_documents")],
        [InlineKeyboardButton(f"{products}", callback_data="info_products"),
         InlineKeyboardButton(f"{collaboration}", callback_data="info_collaboration")],
        [InlineKeyboardButton(f"{news}", callback_data="info_news"),
         InlineKeyboardButton(f"{marketing}", callback_data="info_marketing")],
        [InlineKeyboardButton(f"{back}", callback_data="main_menu")]
    ])
    return kb


def about_j2m_kb(lang) -> InlineKeyboardMarkup:
    documents, products, collaboration, news, marketing, back = [
        "Документы", "Продукты",
        "Сотрудничество", "Новости", "Маркетинг (PDF)", "Главное меню"]
    if lang == "EN":
        documents, products, collaboration, news, marketing, back = [
            "Legal Documents", "Products",
            "Collaboration", "News", "Marketing", "Main Menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{documents}", callback_data="info_documents"),
         InlineKeyboardButton(f"{products}", callback_data="info_products")],
        [InlineKeyboardButton(f"{collaboration}", callback_data="info_collaboration"),
         InlineKeyboardButton(f"{news}", callback_data="info_news")],
        [InlineKeyboardButton(f"{marketing}", callback_data="info_marketing"),
         InlineKeyboardButton(f"{back}", callback_data="main_menu")]
    ])
    return kb


def info_documents_kb(lang) -> InlineKeyboardMarkup:
    dao, products, collaboration, news, marketing, back = [
        "О DAO J2M", "Продукты", "Сотрудничество", "Новости", "Маркетинг", "Главное меню"]
    if lang == "EN":
        dao, products, collaboration, news, marketing, back = [
            "About DAO J2M", "Products", "Collaboration", "News", "Marketing", "Main Menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{dao}", callback_data="dao"),
         InlineKeyboardButton(f"{products}", callback_data="info_products")],
        [InlineKeyboardButton(f"{collaboration}", callback_data="info_collaboration"),
         InlineKeyboardButton(f"{news}", callback_data="info_news")],
        [InlineKeyboardButton(f"{marketing}", callback_data="info_marketing"),
         InlineKeyboardButton(f"{back}", callback_data="main_menu")]
    ])
    return kb


def info_products_kb(lang) -> InlineKeyboardMarkup:
    dao_bot, nft, back = "О боте DAO J2М", "NFT — 10 USDT", "Вернуться в раздел с информацией"
    if lang == "EN":
        dao_bot, nft, back = 'About J2M Bot', 'NFT - 10 USDT', 'Return to Information'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{dao_bot}", callback_data="info_dao_bot"),
         InlineKeyboardButton(f"{nft}", callback_data="info_nft")],
        [InlineKeyboardButton(f"{back}", callback_data="information")]
    ])
    return kb


def info_news_kb(lang) -> InlineKeyboardMarkup:
    group, main, back = "J2M Channel", "Главное меню", "Вернуться в раздел с информацией"
    if lang == "EN":
        group, main, back = "J2M Channel", 'Main Menu','Return to Information'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{group}", url='https://t.me/J2M_Channel')],
        [InlineKeyboardButton(f"◀️ {back}", callback_data="information")],
        [InlineKeyboardButton(f"{main}", callback_data="main_menu")]
    ])
    return kb


def info_bot_nft_kb(lang) -> InlineKeyboardMarkup:
    main, back, product = "Вернуться в главное меню", "Вернуться в раздел с информацией", \
        "Вернуться к описанию продуктов"
    if lang == "EN":
        main, back, product = 'Return to main menu', 'Return to Information', 'Return to Products'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{back}", callback_data="information")],
        [InlineKeyboardButton(f"{main}", callback_data="main_menu")],
        [InlineKeyboardButton(f"{product}", callback_data="info_products")]
    ])
    return kb


def info_collaboration_kb(lang) -> InlineKeyboardMarkup:
    main, back, partners = "Вернуться в главное меню", "Вернуться в раздел с информацией", \
        "Партнеры DAO"
    if lang == "EN":
        main, back, partners = 'Return to main menu', 'Return to Information', 'DAO Partners'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{back}", callback_data="information")],
        [InlineKeyboardButton(f"{main}", callback_data="main_menu")],
        [InlineKeyboardButton(f"{partners}", callback_data="dao_partners")]
    ])
    return kb


def info_marketing_kb(lang) -> InlineKeyboardMarkup:
    gloss, product_pres, partners_pres, instructions, online_resources, webinars, visuals, back = "Глоссарий", \
        "Как заработать с DAO J2M", "Финансовый инструмент", 'Инструкции', 'О сообществе', \
        'Ссылки на ролики и записи вебинаров', 'Визуалы и креативы', 'Назад'
    if lang == "EN":
        gloss, product_pres, partners_pres, instructions, online_resources, webinars, visuals, back = "Glossary", \
            "Product Presentation", "Affiliate Program Presentation", "Instructions", \
            "Links to Online Resources of DAO j2M", "Links to Videos and Webinar Recordings", \
            "Visuals and Creatives", "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{gloss}", callback_data="gloss")],
        [InlineKeyboardButton(f"{product_pres}", callback_data="product_pres")],
        [InlineKeyboardButton(f"{partners_pres}", callback_data="partners_pres")],
        [InlineKeyboardButton(f"{instructions}", callback_data="instructions")],
        [InlineKeyboardButton(f"{online_resources}", callback_data="online_resources")],
        [InlineKeyboardButton(f"{webinars}", callback_data="webinars")],
        [InlineKeyboardButton(f"{visuals}", callback_data="visuals")],
        [InlineKeyboardButton(f"{back}", callback_data="information")]
    ])
    return kb


def media_program() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Перевести баланс на коллективный аккаунт", callback_data="media_transfer")]
    ])
    return kb