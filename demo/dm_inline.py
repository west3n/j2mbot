from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def dm_main_menu(lang) -> InlineKeyboardMarkup:
    balance, refill, withdrawal, structure, support, information = ["Баланс", "⬆️ Пополнение", "Вывод",
                                                                    "Партнерская программа", "Поддержка",
                                                                    "Информация"]
    if lang == "EN":
        balance, refill, withdrawal, structure, support, information = ["Balance", "⬆️ Refill", "Withdrawal",
                                                                        "Affiliate program", "Support",
                                                                        "Information"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'💵 {balance}', callback_data='dm_balance')],
        [InlineKeyboardButton(f'🪪 {structure}', callback_data='structure')],
        [InlineKeyboardButton(f' {refill}', callback_data='dm_refill')],
        [InlineKeyboardButton(f'⬇️ {withdrawal}', callback_data='dm_withdrawal')],
        [InlineKeyboardButton(f'🧑‍💻 {support}', callback_data='support'),
         InlineKeyboardButton(f'📒 {information}', callback_data='information')]
    ])
    return kb


def dm_balance_history(lang) -> InlineKeyboardMarkup:
    refill_history, withdrawal_history, back = ["История пополнений", "История выводов", "Главное меню"]
    if lang == "EN":
        refill_history, withdrawal_history, back = ["Refill history", "Withdrawal history", "Main menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'⬆️ {refill_history}', callback_data='dm_refill_history'),
         InlineKeyboardButton(f'⬇️ {withdrawal_history}', callback_data='dm_withdrawal_history')],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_main_menu')]
    ])
    return kb


def dm_back_button(lang) -> InlineKeyboardMarkup:
    button = 'Главное меню'
    if lang == "EN":
        button = "Main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'◀️ {button}', callback_data='dm_main_menu')]
    ])
    return kb


def dm_refill_main_menu(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3 = "Изучить условия", "Пополнить баланс", "Вернуться в главное меню"
    if lang == "EN":
        button, button_2, button_3 = "To review the terms", "To deposit funds", "Return to main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"‍🎓️ {button}", callback_data="dm_review_terms"),
         InlineKeyboardButton(f"💵 {button_2}", callback_data="dm_deposit_funds")],
        [InlineKeyboardButton(f"◀️ {button_3}", callback_data="dm_main_menu")]
    ])
    return kb


def dm_refill_account_2(lang) -> InlineKeyboardMarkup:
    first_button, second_button, back = "Личный аккаунт от 15 000 USDT", "Коллективный аккаунт от 500 USDT", \
        "Назад"
    if lang == "EN":
        first_button, second_button, back = "Personal account starting from 15,000 USDT", \
            "Collective account starting from 500 USDT.", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="dm_15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="dm_500")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_refill')]
    ])
    return kb


def dm_distribution(lang) -> InlineKeyboardMarkup:
    button, back = "Условия применения ПО", "Назад"
    if lang == "EN":
        button, back = "Terms of software usage", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👪 {button}", callback_data="dm_distribution")],
        [InlineKeyboardButton(f"◀️ {back}", callback_data="dm_refill")]])
    return kb


def dm_refill_account_3(lang) -> InlineKeyboardMarkup:
    first_button, second_button, back = "Личный аккаунт от 15 000 USDT", "Коллективный аккаунт от 500 USDT", \
        "Назад"
    if lang == "EN":
        first_button, second_button, back = "Personal account starting from 15,000 USDT", \
            "Collective account starting from 500 USDT.", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="dm_active_15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="dm_active_500")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_review_terms')]
    ])
    return kb


def dm_active_500(lang) -> InlineKeyboardMarkup:
    button, button_2, back = "Разместить активы коллективный аккаунт", "Изучить условия от 15 000 USDT", "Назад"
    if lang == "EN":
        button, button_2, back = "Place assets in a collective account", \
            "Explore conditions starting from 15,000 USDT", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💵 {button}", callback_data="dm_500")],
        [InlineKeyboardButton(f"📖 {button_2}", callback_data="dm_active_15000")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_distribution')]
    ])
    return kb


def dm_active_15000(lang) -> InlineKeyboardMarkup:
    button, button_2, back = "Разместить активы личный аккаунт", "Изучить условия от 500 USDT", "Назад"
    if lang == "EN":
        button, button_2, back = "Place assets in a personal account", "Explore conditions starting from 500 USDT", \
            "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💵 {button}", callback_data="dm_15000")],
        [InlineKeyboardButton(f"📖 {button_2}", callback_data="dm_active_500")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_distribution')]
    ])
    return kb


def dm_yesno(lang) -> InlineKeyboardMarkup:
    yes_button, no_button = "Да", "Нет"
    if lang == "EN":
        yes_button, no_button = "Yes", "No"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"👍 {yes_button}", callback_data="dm_yes"),
         InlineKeyboardButton(f"👎 {no_button}", callback_data="dm_no")]
    ])
    return kb


def dm_user_terms(lang) -> InlineKeyboardMarkup:
    text = "Принимаю"
    if lang == "EN":
        text = "Accept"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{text}", callback_data='dm_terms_accept')]
    ])
    return kb


def dm_user_terms_2(lang) -> InlineKeyboardMarkup:
    text, text2 = ["Принимаю", "Подтвердить"]
    if lang == "EN":
        text, text2 = ["Accept", "Confirm"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {text}", callback_data='dm_terms_accept')],
        [InlineKeyboardButton(f"{text2}", callback_data="dm_terms_done")]
    ])
    return kb


def dm_emailing_documents(lang) -> InlineKeyboardMarkup:
    button = "Документы отправлены"
    if lang == "EN":
        button = "The documents have been sent"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📨 {button}", callback_data="dm_emailing_documents")]])
    return kb


def dm_emailing_alias(lang) -> InlineKeyboardMarkup:
    button = "Информация отправлена"
    if lang == "EN":
        button = "The information have been sent"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📨 {button}", callback_data="dm_emailing_alias")]])
    return kb


def back_menu(lang) -> InlineKeyboardMarkup:
    button = 'Назад'
    if lang == "EN":
        button = "Back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'◀️ {button}', callback_data='dm_back')]
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
        [InlineKeyboardButton(f"✅ {button}", callback_data="dm_finish_payment")],
        [InlineKeyboardButton(f"❌ {button2}", callback_data="dm_cancel_payment")]
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
        [InlineKeyboardButton(f"🔄 {button}", callback_data="dm_transaction_status"),
         InlineKeyboardButton(f"🧩 {button_2}", callback_data="dm_transaction_detail")],
        [InlineKeyboardButton(f"❌ {button3}", callback_data="dm_cancel_payment")]
    ])
    return kb


def main_withdraw(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3, button_4 = "Вывод средств", "Изменить кошелек для вывода", \
        "Изменить процент реинвестирования", "Вернуться в главное меню"
    if lang == "EN":
        button, button_2, button_3, button_4 = "Withdraw funds", "Change wallet", \
            "Change reinvestment percentage", "Back to main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"🔽 {button}", callback_data="dm_withdrawal_funds")],
        [InlineKeyboardButton(f"🔀 {button_2}", callback_data="dm_change_wallet")],
        [InlineKeyboardButton(f"🧮 {button_3}", callback_data="dm_change_percentage")],
        [InlineKeyboardButton(f"◀️ {button_4}", callback_data="dm_main_menu")]
    ])
    return kb


def withdraw_percentage(lang) -> InlineKeyboardMarkup:
    button, button_2, button_3 = "Ничего", "50%", "100%"
    if lang == "EN":
        button, button_2, button_3 = "None", "50%", "100%"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{button}", callback_data="dm_0"),
         InlineKeyboardButton(f"{button_2}", callback_data="dm_50"),
         InlineKeyboardButton(f"{button_3}", callback_data="dm_100")]
    ])
    return kb


def withdrawal_account(lang) -> InlineKeyboardMarkup:
    first_button, second_button, back = "Вывод с личного аккаунта (от 15 000 USDT)", \
        "Вывод с коллективного аккаунта (от 500 USDT)", "Назад"
    if lang == "EN":
        first_button, second_button, back = "Withdrawal from personal account (starting from 15,000 USDT)", \
            "Withdrawal from collective account (starting from 500 USDT)", "Go back"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="dm_withdrawal_15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="dm_withdrawal_500")],
        [InlineKeyboardButton(f'◀️ {back}', callback_data='dm_withdrawal')]
    ])
    return kb


def finish_withdrawal(lang) -> InlineKeyboardMarkup:
    button, button_2 = "Подтвердить", "Отменить"
    if lang == "EN":
        button, button_2 = "Confirm", "Cancel"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {button}", callback_data="dm_confirm_withdrawal"),
         InlineKeyboardButton(f"❌ {button_2}", callback_data="dm_cancel_withdrawal")]
    ])
    return kb
