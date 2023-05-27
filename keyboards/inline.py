from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(lang) -> InlineKeyboardMarkup:
    balance, refill, withdrawal, structure, support, information = ["Баланс", "Пополнение", "Вывод", "Структура",
                                                                    "Поддержка", "Информация"]
    if lang == "EN":
        balance, refill, withdrawal, structure, support, information = ["Balance", "Refill", "Withdrawal", "Structure",
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


def back_button(lang) -> InlineKeyboardMarkup:
    button = 'Вернуться назад'
    if lang == "EN":
        button = "Return"
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
    refill_history, withdrawal_history, back = ["История пополнений", "История выводов", "Вернуться назад"]
    if lang == "EN":
        refill_history, withdrawal_history, back = ["Refill history", "Withdrawal history", "Return"]
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
    text = "Принимаю"
    text2 = "Подтвердить"
    if lang == "EN":
        text = "Accept"
        text2 = "Confirm"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"✅ {text}", callback_data='terms_accept')],
        [InlineKeyboardButton(f"{text2}", callback_data="terms_done")]
    ])
    return kb


def information_menu(lang) -> InlineKeyboardMarkup:
    distribution, conditions, urls, docs, back = [
        "Распределение доходности", "Условия пополнения и вывода",
        "Важные ссылки", "Документация", "Вернуться назад"]
    if lang == "EN":
        distribution, conditions, urls, docs, back = [
            "Distribution of profitability", "Terms of replenishment and withdrawal",
            "Important links", "Documentation", "Go back"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{distribution}", callback_data="distribution")],
        [InlineKeyboardButton(f"{conditions}", callback_data="conditions")],
        [InlineKeyboardButton(f"{urls}", callback_data=urls),
         InlineKeyboardButton(f"{docs}", callback_data=docs)],
    ])
    return kb
