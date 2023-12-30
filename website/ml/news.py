import csv
import json
import re
import requests
import pandas as pd

from dotenv import load_dotenv
from easygoogletranslate import EasyGoogleTranslate
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



load_dotenv()

# nltk.download('stopwords')
# nltk.download('wordnet')

class APIRequestError(RequestException):
    pass


API_KEY = "s67fd6sg67asd67g4sdd3gahfgsdl26875768dfasfsf78sdg78s8g89l568"


def api_call(endpoint, params=None, json=None, type="get"):
    # Specify the API endpoint URL
    api_url = f"http://backend:1111/{endpoint}"

    # Make a GET request to the API
    if type == "get":
        response = requests.get(
            api_url, headers={"api_key": API_KEY}, params=params, json=json
        )
    if type == "post":
        response = requests.post(
            api_url, headers={"api_key": API_KEY}, params=params, json=json
        )
    if type == "put":
        response = requests.put(
            api_url, headers={"api_key": API_KEY}, params=params, json=json
        )
    if type == "delete":
        response = requests.delete(
            api_url, headers={"api_key": API_KEY}, params=params, json=json
        )

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and use the response data (assuming it's in JSON format)
        data = response.json()
        return data
    else:
        # Print an error message if the request was not successful
        raise APIRequestError(f"Error: {response.status_code} - {response.text}")


preprocessed_text = []
translated_text = []

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def translate_text(text):
    return translator.translate(text)


# TR -> EN
translator = EasyGoogleTranslate(source_language="tr", target_language="en", timeout=10)

# EN -> TR
translatorR = EasyGoogleTranslate(
    source_language="en", target_language="tr", timeout=10
)


def preprocess(text_to_preprocess):
    for i in text_to_preprocess:
        if isinstance(i, str):  # Kontrol et, hücre bir string mi?
            preprocessed_text.append(" ".join(i.split()))
        else:
            preprocessed_text.append("")  # NaN ise boş bir string ekle
    return preprocessed_text


def preprocess_text(text):
    if pd.isna(text):  # Check if the text is NaN
        return ""
    return text


def _create_dictionary_table(text_string) -> dict:
    words = re.findall(
        r"\b\w+\b", text_string.lower()
    )  # Extract words, convert to lowercase
    # Creating a dictionary for the word frequency table
    frequency_table = dict()
    for wd in words:
        wd = lemmatizer.lemmatize(wd)
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table


def _calculate_sentence_scores(sentences, frequency_table, filter_keywords) -> dict:
    # Algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        # Check if the sentence contains any of the filter keywords
        if any(keyword.lower() in sentence.lower() for keyword in filter_keywords):
            sentence_wordcount = len(
                re.findall(r"\b\w+\b", sentence.lower())
            )  # Extract words, convert to lowercase
            sentence_wordcount_without_stop_words = 0
            key = sentence  # Use the entire sentence as a key
            for word_weight in frequency_table:
                if word_weight.lower() in sentence.lower():
                    sentence_wordcount_without_stop_words += 1
                    if key in sentence_weight:
                        sentence_weight[key] += frequency_table[word_weight]
                    else:
                        sentence_weight[key] = frequency_table[word_weight]

            sentence_weight[key] = (
                sentence_weight[key] / sentence_wordcount_without_stop_words
            )

    return sentence_weight


def _get_article_summary(sentences, sentence_weight, threshold):
    if not sentence_weight:
        return "No summary available"  # You can choose an appropriate default value
    max_score_sentence = max(sentence_weight, key=sentence_weight.get)
    return max_score_sentence


def _run_article_summary(article):
    # Define keywords to filter sentences
    filter_keywords = [
        "date",
        "place",
        "location",
        "increase",
        "decrease",
        "market",
        "price",
        "rate",
        "decision",
        "value",
        "dollar",
        "euro",
        "gold",
    ]

    # Tokenizing the sentences
    sentences = sent_tokenize(article)

    # Creating a dictionary for the word frequency table
    frequency_table = _create_dictionary_table(article)

    # Algorithm for scoring sentences by their words
    sentence_scores = _calculate_sentence_scores(
        sentences, frequency_table, filter_keywords
    )

    # Getting the threshold
    threshold = (
        1.2 * sum(sentence_scores.values()) / len(sentence_scores)
        if len(sentence_scores) > 0
        else 0
    )

    # Producing the summary
    article_summary = _get_article_summary(sentences, sentence_scores, threshold)

    return article_summary


def extract_and_process():
    # Firefox tarayıcısını başlat
    driver = webdriver.Firefox()

    # Bloomberg'ten veri çekme
    bloomberght_url = "https://www.bloomberght.com/haberler"
    driver.get(bloomberght_url)
    bloomberght_links = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-newscategory="Haberler"]')
        )
    )
    bloomberght_urls = [link.get_attribute("href") for link in bloomberght_links]

    # Mynet Finans'tan veri çekme
    mynet_url = "https://finans.mynet.com/haber/kategori/borsa/"
    driver.get(mynet_url)
    mynet_links = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-body h3 a"))
    )
    mynet_urls = [link.get_attribute("href") for link in mynet_links]

    # Tarayıcıyı kapatın
    driver.quit()

    # CSV dosyasını oluştur
    with open("haber_metinleri.csv", "w", encoding="utf-8", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Haber Metni", "URL"])

        # Haber metinlerini çekmek için aynı tarayıcıyı yeniden başlat
        driver = webdriver.Firefox()

        # Bloomberg'ten veri çekme
        for url in bloomberght_urls:
            driver.get(url)
            try:
                news_item = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".news-item"))
                )
                news_text = news_item.text
                csv_writer.writerow([news_text, url])
            except:
                print("Bloomberg'ten haber metni bulunamadı.")

        # Mynet Finans'tan veri çekme
        for url in mynet_urls:
            driver.get(url)
            try:
                news_paragraphs = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".detail-content-inner p")
                    )
                )

                news_text = [paragraph.text for paragraph in news_paragraphs]
                combined_text = "".join(news_text)
                # print(combined_text)
                csv_writer.writerow([combined_text, url])
            except:
                print("Mynet Finans'tan haber metni bulunamadı.")

        # Tarayıcıyı kapat
        driver.quit()
    df = pd.read_csv("haber_metinleri.csv", encoding="utf-8")
    all_texts = df["Haber Metni"]
    preprocess(all_texts)

    # Her bir metni çevirin ve sonucu "translated" listesine ekle
    for i in preprocessed_text:
        try:
            if len(i) <= 5000:
                translated_text.append(translator.translate(i))
            else:
                chunks = [i[x : x + 5000] for x in range(0, len(i), 5000)]
                chunk_translations = [translator.translate(chunk) for chunk in chunks]
                translated_text.append(" ".join(chunk_translations))
        except:
            translated_text.append("NULL")
            continue

    # CSV dosyasını güncelleyin
    df["Translated Text"] = translated_text
    df["Özet"] = ""

    i = 0
    for new in df["Translated Text"]:
        summary = _run_article_summary(new)
        df["Özet"][i] = translatorR.translate(summary)
        i += 1

    df_filtered = df[df["Özet"] != "Özet mevcut değil"]

    json_data = (
        df_filtered.to_json(orient="records", force_ascii=False, indent=2)
        .encode("utf-8")
        .decode("utf-8")
    )

    return json_data


if __name__ == "__main__":
    json_result = extract_and_process()
    data_list = json.loads(json_result)
    for data_dict in data_list:
        api_call(
            endpoint="news/add_news",
            params={
                "news_information": data_dict["Özet"],
                "news_link": data_dict["URL"],
            },
            type="post",
        )
