import requests
from bs4 import BeautifulSoup
import json
import random


def scrape_HTML(url):
    response = requests.get(url)
    html = response.content
    return BeautifulSoup(html, 'html.parser')


def extract_conversation(soup, conversation_id):
    conversations = []
    soru_scraped = False
    # Find all <div> elements with class "soru"
    for soru_div in soup.find_all('div', class_='soru'):
        # Get the text content of the first <div> element with class "col-lg-12 bizimFont" inside this <div>
        soru_content_div = soru_div.find('div', class_='col-lg-12 bizimFont')
        if soru_content_div is not None:
            soru_content = soru_content_div.get_text(strip=True)
            # Add the soru content to the conversations list as a "soru" message
            if not soru_scraped:
                conversations.append({
                    "from": "soru",
                    "value": soru_content
                })
                soru_scraped = True
            else:
                conversations.append({
                    "from": "cevap",
                    "value": soru_content
                })
    # Create a conversation JSON object with the given ID and the extracted messages
    conversation = {
        "id": conversation_id,
        "conversations": conversations
    }

    return conversation


def scrape_qa_page(page_number, page_outputs):
    print(f'scraping page number {page_number}...')
    # we are adding the random bit at the end to prevent cached response from the website
    url = f'https://risale.online/soru-cevap?p={page_number}&random={random.randint(0, 100000)}'
    page_soup = scrape_HTML(url)
    # Find all <div> elements with class "soru"
    divs = page_soup.find_all('div', class_='soru')

    # Loop through the <div> elements and call the extract_conversation method with the desired URL
    for div in divs:
        # Find the first <a> tag
        a_tag = div.find('a')
        if a_tag:
            question_url = "https://risale.online" + a_tag['href']
            print(question_url)
            conversation_id = question_url.split('/')[-1]
            conversation = extract_conversation(scrape_HTML(question_url), conversation_id)
            page_outputs.append(conversation)


def scrape_all_until(last_page):
    all_outputs = []
    for page_number in range(last_page):
        scrape_qa_page(page_number + 1, all_outputs)
    return all_outputs


while True:
    try:
        number_of_pages = int(input("Kaç sayfalık soru-cevap çekmek istersiniz: "))
        if number_of_pages <= 0 or number_of_pages > 345:
            raise ValueError
        break
    except ValueError:
        print("Lütfen geçerli bir sayı girin (0 < sayfa sayısı < 346)")

outputs = scrape_all_until(number_of_pages)

# Write the output conversations to a JSON file
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(outputs, f, ensure_ascii=False, indent=4)


