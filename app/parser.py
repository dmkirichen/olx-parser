import requests
import itertools
from threading import Thread
from bs4 import BeautifulSoup
from app.models import Advertisement
from app import db

BASE_URL = "https://www.olx.ua"
CATEGORY_URL = "https://www.olx.ua/d/uk/zhivotnye/"


def parse_ad(ad_url):
    # Loading ad page
    r = requests.get(ad_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        imgs = soup.find_all('img')
        image = imgs[0]["src"]

        h1s = soup.find_all('h1')
        title = h1s[0].text

        h3s = soup.find_all('h3')
        price = h3s[0].text

        h4s = soup.find_all('h4')
        salesman = h4s[0].text
    except IndexError:
        # Some elements are missing.
        # Will ignore such ads for now.
        return False

    print(f"adding: {title} - {price} - {salesman} - {image}")
    # Check if such ad is already in database
    ad = Advertisement.query.filter_by(title=title, salesman=salesman, price=price).first()
    if ad:  # ad with such info already exists
        return False

    # Adding new ad to the database
    new_ad = Advertisement(title=title, salesman=salesman, price=price, image=image)
    db.session.add(new_ad)
    db.session.commit()
    return True


def parse_category(category_url, stop_after=300):
    all_rel_links = []
    for i in itertools.count():
        # Loading category page
        r = requests.get(category_url, params={"page": i})
        soup = BeautifulSoup(r.content, 'html.parser')

        # Extracting all links from the web page
        links = [a.get('href') for a in soup.find_all('a')]

        # Leaving only links with products
        relevant_links = [BASE_URL + link for link in links if "/d/uk/obyavlenie/" in link]

        # Process every ad in separate thread
        for rel_link in relevant_links:
            t = Thread(target=parse_ad, args=(rel_link,))
            t.start()

        all_rel_links += relevant_links
        if len(all_rel_links) > stop_after:  # we got enough entries from the category
            break
    return all_rel_links


# if __name__ == '__main__':
#     parse_category(CATEGORY_URL)
