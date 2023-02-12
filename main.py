import csv
from typing import List
from selenium import webdriver
from time import sleep
from dataclasses import dataclass, astuple, fields
from bs4 import BeautifulSoup, Tag

URL = "https://www.zooplus.de/tierarzt/results?animal_99=true"
NUM_PAGES = 5

driver = webdriver.Chrome()


@dataclass
class Veterinarian:
    name: str
    clinic: str
    reception_time: str
    address: str
    rating: int
    num_reviews: int


VETERINARIAN_FIELDS = [field.name for field in fields(Veterinarian)]


def parse_single_veterinarian(page_soup: BeautifulSoup | Tag) -> Veterinarian:
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


def get_single_page_veterinarian(page_soup: BeautifulSoup) -> List[Veterinarian]:
    veterinarians = page_soup.select(".result-intro__details")
    return [parse_single_veterinarian(soup) for soup in veterinarians]


def get_veterinarians(url) -> List[Veterinarian]:
    driver.get(url)
    sleep(3)
    page = driver.page_source
    first_page_soup = BeautifulSoup(page, "lxml")
    veterinarians = get_single_page_veterinarian(first_page_soup)
    for page_num in range(2, NUM_PAGES + 1):
        driver.get(f"{url}&page={page_num}")
        sleep(2.5)
        page = driver.page_source
        soup = BeautifulSoup(page, "lxml")
        veterinarians.extend(get_single_page_veterinarian(soup))
    return veterinarians


def write_to_csv(veterinarians: [Veterinarian], name: str):
    with open(f"{name}.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(VETERINARIAN_FIELDS)
        writer.writerows([astuple(v) for v in veterinarians])


def main():
    test = get_veterinarians(URL)
    write_to_csv(test, "veterinarians")


if __name__ == "__main__":
    main()
    driver.close()
    driver.quit()
