from num2words import num2words
from decimal import Decimal, ROUND_HALF_UP

def currency_word(rubles, kopecks):
    """Склонение валют"""
    # Проверка для рублей
    if rubles == 0:
        declension_ruble_word = "рублей"
    elif rubles % 10 == 1 and rubles % 100 != 11:
        declension_ruble_word = "рубль"
    elif 2 <= rubles % 10 <= 4 and (rubles % 100 < 10 or rubles % 100 >= 20):
        declension_ruble_word = "рубля"
    else:
        declension_ruble_word = "рублей"

    # Проверка для копеек
    if kopecks == 0:
        declension_kopecks_word = "копеек"
    elif kopecks % 10 == 1 and kopecks % 100 != 11:
        declension_kopecks_word = "копейка"
    elif 2 <= kopecks % 10 <= 4 and (kopecks % 100 < 10 or kopecks % 100 >= 20):
        declension_kopecks_word = "копейки"
    else:
        declension_kopecks_word = "копеек"

    return declension_ruble_word, declension_kopecks_word

def number_to_words(value):
    """Преобразование числа в слова с валютами"""
    try:
        parts = str(value).split('.')
        rubles = int(parts[0])
        
        if len(parts) > 1:
            kopecks_str = parts[1]
            if len(kopecks_str) == 1:
                kopecks_str += '0'
            kopecks = int(kopecks_str)
        else:
            kopecks = 0 
    
        declension_ruble_word, declension_kopecks_word = currency_word(rubles, kopecks)

        rubles_words = num2words(rubles, lang='ru') + f" {declension_ruble_word}"
        kopecks_formatted = f"{kopecks:02d}"
        kopecks_words = f" {kopecks_formatted} {declension_kopecks_word}"
        
        return rubles_words + kopecks_words
    except Exception as e:
        return f"Ошибка преобразования числа: {str(e)}"