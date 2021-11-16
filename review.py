from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import csv
import os

########## Configuration ##########

PRODUCT_URLS = []
NO_COMMENT_PER_RATING = 50
FILENAME = 'dataset/reviews.csv'
COLUMNS = ['review', 'rating']

######################################################


def toint(val):
    try:
        return int(val)
    except:
        return None


def export_csv(val):
    os.makedirs(os.path.dirname(FILENAME), exist_ok=True)

    with open(FILENAME, 'w') as f:
        write = csv.writer(f)
        write.writerow(COLUMNS)
        write.writerows(val)


def main():
    reviews = []

    service = Service(ChromeDriverManager().install())
    wd = webdriver.Chrome(service=service)

    for i, product_url in enumerate(PRODUCT_URLS):
        wd.get(product_url)

        WebDriverWait(wd, 30).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'product-briefing')))

        print('scraping ... {}'.format(wd.title))

        if i == 0:
            popup = wd.find_element(
                By.CSS_SELECTOR, '.language-selection__list-item')
        else:
            popup = None

        if (popup):
            btn = wd.find_element(
                By.XPATH, '//*[@id="modal"]/div[1]/div[1]/div/div[3]/div[1]/button')
            btn.click()

        wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        WebDriverWait(wd, 30).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'product-rating-overview')))
        wd.execute_script(
            "document.getElementsByClassName('product-rating-overview')[0].scrollIntoView()")

        ratings = wd.find_elements(
            By.CSS_SELECTOR, '.product-rating-overview__filter')

        next_btn = wd.find_element(
            By.CSS_SELECTOR, '.shopee-icon-button.shopee-icon-button--right')

        for rating in ratings:
            score = toint(rating.text[0])
            rating.click()

            if score is None:
                continue

            print('scraping rating ... ({})'.format(score))

            num = 0
            while num < NO_COMMENT_PER_RATING:
                WebDriverWait(wd, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'shopee-product-rating')))

                comments = wd.find_elements(
                    By.CSS_SELECTOR, '.shopee-product-rating')

                print('scraping comment: {}'.format(num))

                for comment in comments:
                    review = comment.find_element(
                        By.CLASS_NAME, 'shopee-product-rating__content')

                    reviews.append([review.text, score])
                    num += 1

                next_btn.click()

    wd.close()
    wd.quit()

    print('exporting to csv file')
    export_csv(reviews)


if __name__ == '__main__':
    main()
