import pymorphy2
import requests


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


# Получить название населенного пункта по координатам
def ai_get_location(img_url):
    url = "https://picarta.ai/classify"
    api_token = "E60DJWHVWY7YXDXT5V37"
    headers = {"Content-Type": "application/json"}

    payload = {"TOKEN": api_token,
               "IMAGE": img_url}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        lat, lon = round(result["ai_lat"], 6), round(result["ai_lon"], 6)
        geo_apikey = '40d1649f-0493-4b70-98ba-98533de7710b'
        geocoder_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={geo_apikey}&geocode={lon},{lat}&format=json"
        response = requests.get(geocoder_url)
        return response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["Address"]["Components"][3]["name"]
    else:
        return None
