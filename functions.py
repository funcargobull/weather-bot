import pymorphy2


# Начальная форма слова
def normal_form(word):
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(word)[0].normal_form


# Проверка текста на город по общей базе
def check_if_city(prompt, CITIES):
    s = [normal_form(w).translate(str.maketrans('', '', "!#$%&'()*+,./:;<=>?@[\]^_`{|}~")) for w in prompt.split()]
    word = " ".join(s)
    if word + "\n" in CITIES or word in CITIES:
        return True, word.title()
    for i in s:
        if i + "\n" in CITIES or i in CITIES:
            return True, i.title()
    return False, 0
