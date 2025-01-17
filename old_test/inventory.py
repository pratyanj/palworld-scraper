import os
import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from time import sleep
from playwright.sync_api import sync_playwright
import customtkinter as ctk

class PalDetails:
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def fetch_url(self, url, timeout=120):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = self.session.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch URL {url}: {e}")
            return None
    
    def get_soup(self, url):
        response = self.fetch_url(url)
        if response:
            return BeautifulSoup(response.text, 'html.parser')
        return None
    
    def download_image(self, image_url, save_path):
        download_path = os.path.join(os.getcwd(), "images", f"{save_path}.png")
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        response = requests.get(image_url)
        if response.status_code == 200:
            print(f"Downloading image from: {image_url}")
            with open(download_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    
    def extract_stats(self, soup, rarity):
        stats = {}
        stat_rows = soup.select("div.card-body div.d-flex.justify-content-between.p-2")
        for row in stat_rows:
            try:
                name = row.select_one('div:first-child').text.strip()
                try:
                    value = int(row.select_one('div:last-child').text.strip())
                except:
                    value = row.select_one('div:last-child').text.strip()
                if name not in stats:
                    stats[name] = value
                    print(f"{name}: {value}")
            except Exception as e:
                print(f"Error processing stat row: {e}")
                continue
        return stats
    
    def fetch_item_details(self, item_type, url):
        soup = self.get_soup(url)
        items = []
        if soup:
            item_cards = soup.find_all('div', class_='card itemPopup')
            counter = 0
            for card in item_cards:
                item = {}
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                counter += 1
                item['ID'] = counter
                name_element = card.find('a', class_='itemname')
                item['name'] = name_element.text.strip() if name_element else ''
                for i in range(5):
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        item['rarity'] = rarity_element.text.strip()
                        break
                desc_element = card.find('div', class_='card-body')
                item['description'] = desc_element.text.strip() if desc_element else ''
                img_element = card.find('img', loading='lazy')
                item['image'] = f"../assets/images/items/{item['name'].replace(' ', '-').lower()}.png"
                item['image_url'] = img_element['src'] if img_element else ''
                sts = self.extract_stats(soup, item['rarity'])
                if sts:
                    item['stats'] = sts
                items.append(item)
            with open(f"{item_type}.json", "w") as f:
                json.dump(items, f, indent=2)
        return items

    def get_weapon(self):
        return self.fetch_item_details('weapon', 'https://paldb.cc/en/Weapon')

    def get_sphere(self):
        return self.fetch_item_details('sphere', 'https://paldb.cc/en/Sphere')

    def get_sphere_module(self):
        return self.fetch_item_details('sphere_module', 'https://paldb.cc/en/Sphere_Module')

    def get_armor(self):
        return self.fetch_item_details('armor', 'https://paldb.cc/en/Armor')

    def get_accessory(self):
        return self.fetch_item_details('accessory', 'https://paldb.cc/en/Accessory')

    def get_material(self):
        return self.fetch_item_details('material', 'https://paldb.cc/en/Material')

def create_gui():
    def on_select():
        method = method_var.get()
        if method == "Weapon":
            pal_details.get_weapon()
        elif method == "Sphere":
            pal_details.get_sphere()
        elif method == "Sphere Module":
            pal_details.get_sphere_module()
        elif method == "Armor":
            pal_details.get_armor()
        elif method == "Accessory":
            pal_details.get_accessory()
        elif method == "Material":
            pal_details.get_material()
    
    root = ctk.CTk()
    root.title("Scraping Selector")
    
    method_var = ctk.StringVar(value="Weapon")
    methods = ["Weapon", "Sphere", "Sphere Module", "Armor", "Accessory", "Material"]
    
    ctk.CTkLabel(root, text="Select Method:").pack(pady=10)
    ctk.CTkOptionMenu(root, variable=method_var, values=methods).pack(pady=10)
    ctk.CTkButton(root, text="Start Scraping", command=on_select).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    pal_details = PalDetails()
    create_gui()
