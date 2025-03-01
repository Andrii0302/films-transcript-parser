import requests
from bs4 import BeautifulSoup
import re


class Parser:
    __slots__ = ("letter", "pages", "root")

    def __init__(self, letter: str, pages: int):
        self.letter = letter.lower()
        self.pages = int(pages)
        self.root = "https://subslikescript.com"

    @property
    def website(self) -> str:
        return f"{self.root}/movies_letter-{self.letter.upper()}"

    @property
    def soup(self) -> BeautifulSoup:
        """Returns BeautifulSoup object for the base website."""
        response = requests.get(self.website)
        return BeautifulSoup(response.text, "lxml")

    def get_page_soup(self, page: int) -> BeautifulSoup:
        """Fetches and returns BeautifulSoup object for a specific page."""
        url = f"{self.website}?page={page}"
        response = requests.get(url)
        return BeautifulSoup(response.text, "lxml")

    def extract_movie_links(self) -> list[str]:
        """Extracts all movie links from paginated pages."""
        links = []
        for page in range(1, self.pages + 1):
            soup = self.get_page_soup(page)
            box = soup.find("article", class_="main-article")

            if box:
                links.extend(link["href"] for link in box.find_all("a", href=True))

        return links

    def fetch_and_save_script(self, link: str):
        """Fetches movie script from a given link and saves it to a file."""
        url = f"{self.root}/{link}"
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            box = soup.find("article", class_="main-article")

            if box:
                title = re.sub(r'[<>:"/\\|?*]', "", box.find("h1").get_text(strip=True))
                script = box.find("div", class_="full-script").get_text(
                    strip=True, separator=" "
                )

                filename = f"{title}.txt"
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(script)

                print(f"✅ Saved: {filename}")
            else:
                print(f"❌ Skipping {url} (No script found)")

        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")

    def parse(self):
        """Main method to extract and save all movie scripts."""
        print(
            f"🔍 Fetching movie links for '{self.letter.upper()}' across {self.pages} pages..."
        )
        links = self.extract_movie_links()

        if not links:
            print("❌ No movie links found.")
            return

        print(f"📂 Found {len(links)} movie links. Fetching scripts...")
        for link in links:
            self.fetch_and_save_script(link)

        print("✅ Parsing completed.")


if __name__ == "__main__":
    letter = input("Enter the starting letter of the movie title: ")
    pages = input("Enter the number of pages to parse: ")

    parser = Parser(letter, pages)
    parser.parse()
