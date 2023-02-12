import csv
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
from dataclasses import dataclass, astuple, fields
from bs4 import BeautifulSoup

URL = "https://www.zooplus.de/tierarzt/results?animal_99=true"

wd_path = "webdriver/chromedriver.exe"
service = Service(executable_path=wd_path)
driver = webdriver.Chrome(service=service)


@dataclass
class Veterinarian:
    name: str
    clinic: str
    reception_time: str
    address: str
    rating: int
    num_reviews: int


VETERINARIAN_FIELDS = [field.name for field in fields(Veterinarian)]


def parse_single_veterinarian(page_soup: BeautifulSoup) -> Veterinarian:
    try:
        clinic = page_soup.select_one(".result-intro__subtitle").text
    except AttributeError:
        clinic = "-"
    return Veterinarian(
        name=page_soup.select_one(".result-intro__title").text,
        clinic=clinic,
        reception_time=page_soup.select_one(".daily-hours").text,
        address=page_soup.select_one(".result-intro__address").text,
        rating=len(page_soup.select_one(".result-intro__rating__score").select_one(".star-rating ").find_all("span")
                   ),
        num_reviews=int(page_soup.select_one(".result-intro__rating__note").text.split()[0])
    )


def get_single_page_veterinarian(page_soup: BeautifulSoup):
    veterinarians = page_soup.select(".result-intro__details")
    return [parse_single_veterinarian(soup) for soup in veterinarians]


def get_veterinarians(url, num_pages: int) -> [Veterinarian]:
    driver.get(url)
    sleep(3)
    page = driver.page_source
    first_page_soup = BeautifulSoup(page, "lxml")
    veterinarians = get_single_page_veterinarian(first_page_soup)
    for page_num in range(2, num_pages + 1):
        driver.get(f"{url}&page={page_num}")
        sleep(4)
        page = driver.page_source
        soup = BeautifulSoup(page, "lxml")
        veterinarians.extend(get_single_page_veterinarian(soup))
    return list(veterinarians)


def write_to_csv(veterinarians: [Veterinarian], name: str):
    with open(f"{name}.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(VETERINARIAN_FIELDS)
        writer.writerows([astuple(v) for v in veterinarians])


def main():
    test = get_veterinarians(URL, 5)
    write_to_csv(test, "test")
    return test


if __name__ == "__main__":
    main()

driver.close()
driver.quit()
