from pathlib import Path
import timer
import json
import requests


class Parse5ka:
    def __init__(self, start_url: str, products_path: Path):
        self.start_url = start_url
        self.products_path = products_path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.182 Safari/537.36"
        }

    def _get_response(self, url: str):
        while True:
            response = requests.get(url, params=None, headers=self.headers)
            if response.status_code == 200:
                return response
            timer.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            file_name = f"{[product['id']]}.json"
            product_path = self.products_path.joinpath(file_name)
            self.save(product, product_path)

    def _parse(self, url: str):
        response = None
        try:
            while url:
                response = self._get_response(url)
                data = response.json()
                url = data["next"]
                for product in data["results"]:
                    yield product

        except Exception:
            if response is not None:
                print(response.text)
            print(Exception)


@staticmethod
def save(data: dict, file_path):
    file_path.write_text(json.dump(data, ensure_ascii=False), encoding="UTF-8")


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    save_path = Path(__file__).parent.joinpath("products")
    if not save_path.exists():
        save_path.mkdir()

    parser = Parse5ka(url, save_path)
    parser.run()
