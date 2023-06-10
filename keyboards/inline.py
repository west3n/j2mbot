from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(lang) -> InlineKeyboardMarkup:
    balance, refill, withdrawal, structure, support, information = ["Баланс", "Пополнение", "Вывод", "Рефералы",
                                                                    "Поддержка", "Информация"]
    if lang == "EN":
        balance, refill, withdrawal, structure, support, information = ["Balance", "Refill", "Withdrawal", "Referral",
                                                                        "Support", "Information"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'💵 {balance}', callback_data='balance'),
         InlineKeyboardButton(f'🪪 {structure}', callback_data='structure')],
        [InlineKeyboardButton(f'⬆️ {refill}', callback_data='refill'),
         InlineKeyboardButton(f'⬇️ {withdrawal}', callback_data='withdrawal')],
        [InlineKeyboardButton(f'🧑‍💻 {support}', url='https://t.me/J2M_Support'),
         InlineKeyboardButton(f'📒 {information}', callback_data='information')]
    ])
    return kb


def main_menu_short(lang) -> InlineKeyboardMarkup:
    balance, support, information = ["Кошелек", "Поддержка", "Информация"]
    if lang == "EN":
        balance, support, information = ["Wallet", "Support", "Information"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'💵 {balance}', callback_data='balance')],
        [InlineKeyboardButton(f'🧑‍💻 {support}', url='https://t.me/J2M_Support'),
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


def information_menu(lang) -> InlineKeyboardMarkup:
    distribution, conditions, urls, docs, back = [
        "Распределение доходности", "Условия пополнения и вывода",
        "Важные ссылки", "Документация", "Главное меню"]
    if lang == "EN":
        distribution, conditions, urls, docs, back = [
            "Distribution of profitability", "Terms of replenishment and withdrawal",
            "Important links", "Documentation", "Main menu"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{distribution}", callback_data="distribution")],
        [InlineKeyboardButton(f"{conditions}", callback_data="conditions")],
        [InlineKeyboardButton(f"{urls}", callback_data="urls"),
         InlineKeyboardButton(f"{docs}", callback_data="docs")],
        [InlineKeyboardButton(f"◀️ {back}", callback_data="main_menu")]
    ])
    return kb


def referral_statistic(lang) -> InlineKeyboardMarkup:
    text, back = 'Подробная статистика', "Главное меню"
    if lang == "EN":
        text, back = "Detailed statistic", "Main menu"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"📊 {text}", callback_data='full_statistic')],
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
    first_button, second_button = "Личный аккаунт от 15000 USDT", "Коллективный аккаунт от 500 USDT"
    if lang == "EN":
        first_button, second_button = "Personal account starting from 15,000 USDT", \
            "Collective account starting from 500 USDT."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"💰 {first_button}", callback_data="15000")],
        [InlineKeyboardButton(f"💵 {second_button}", callback_data="500")]
    ])
    return kb
