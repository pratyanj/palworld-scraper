import os
import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from  time import sleep
from playwright.sync_api import sync_playwright

def download_image(image_url, save_path):
    download_path = os.path.join(os.getcwd(), "images", f"{save_path}.webp")
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    response = requests.get(image_url)
    if response.status_code == 200:
        print(f"Downloading image from: {image_url}")
        with open(download_path, 'wb') as file:
            file.write(response.content)
        
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
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
        """Fetch a URL with retry logic and return the response."""
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
        """Retrieve and parse the HTML content of a given URL."""
        response = self.fetch_url(url)
        if response:
            return BeautifulSoup(response.text, 'html.parser')
        return None
    
    
    def download_image11(self, image_url, pal_name):
        """Download an image to a local directory."""
        download_path = os.path.join(os.getcwd(), "images", f"{pal_name}.png")
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        while True:
            response = self.fetch_url(image_url)
            if response:
                with open(download_path, 'wb') as f:
                    f.write(response.content)
                print(f"Image downloaded successfully to: {download_path}")
                break
            sleep(1)  # Wait 1 second before retrying
    def stats(self,item_name,rarity:str):
       
        url = f'https://paldb.cc/en/{item_name.replace("+","%2B")}'
        print(url)
       
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch details for {item_name}: {e}")
            return None

        if response.status_code != 200:
            print(f"Failed to retrieve data for {item_name}, HTTP {response.status_code}")
            return None

        # print("Successfully fetched the page content.")
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(f"Soup: {soup}")
        stats = {}
        # if rarity == "Common":
        #     # try:
        #     #     print("Common")
        #     #     stat_rows = soup.select("div#Items div.card-body div.d-flex.justify-content-between.p-2")
        #     # except:
        #     #     print("EXCommon")
        #         stat_rows = soup.select("div.card-body div.d-flex.justify-content-between.p-2")
        # elif rarity == "Uncommon":

        #     stat_rows = soup.select(
        #         "div#Items-1 div.card-body div.d-flex.justify-content-between.p-2")

        # elif rarity == "Rare":

        #     stat_rows = soup.select(
        #         "div#Items-2 div.card-body div.d-flex.justify-content-between.p-2")

        # elif rarity == "Epic":
        #     stat_rows = soup.select(
        #         "div#Items-3 div.card-body div.d-flex.justify-content-between.p-2")

        # elif rarity == "Legendary":

        #     stat_rows = soup.select(
        #         "div#Items-4 div.card-body div.d-flex.justify-content-between.p-2")
            
        # Get all stat rows from the card
        
            
        stat_rows = soup.select("div.card-body div.d-flex.justify-content-between.p-2")
        

        for row in stat_rows:
            try:
                # Get the stat name and value
                name = row.select_one('div:first-child').text.strip()
                try:
                    value = int(row.select_one('div:last-child').text.strip())
                except:
                    value = row.select_one('div:last-child').text.strip()
                
                # Check if the name is in the desired keys
                if name in ['MeleeAttack', 'Attack', 'Defense','SortID','Health',"Gold Coin","Weight",
                            "Durability",'Rarity',"MaxStackCount","SneakAttackRate","Rank",'Code','MagazineSize']:
                    # Only add if the key is not already in stats
                    if name not in stats:
                        stats[name] = value
                        print(f"{name}: {value}")
                else:
                    
                    stats[name] = value
                    print(f"{name}: {value}")
            except Exception as e:
                print(f"Error processing stat row: {e}")
                continue
        # print(f"Stats: {stats}")
        with open("stats.json", "w") as f:
                json.dump(stats, f, indent=2)
        return stats
    
    def get_weapon(self):
        """Retrieve detailed information about all weapons."""
        url = 'https://paldb.cc/en/Weapon'
        soup = self.get_soup(url)
        weapons = []
        
        if soup:
            weapon_cards = soup.find_all('div', class_='card itemPopup')
            counter = 0
            for card in weapon_cards:
                weapon = {}
                
                # Check if weapon is available
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                                
                counter += 1
                weapon['ID'] = counter
                # Extract weapon name
                name_element = card.find('a', class_='itemname')
                weapon['name'] = name_element.text if name_element else ''
                print(f"Weapon name: {weapon['name']}")
                # Extract weapon type and rarity
                for i in range(5):  # 0-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        weapon['rarity'] = rarity_element.text.strip()
                        break
                              
                # Extract attack value
                attack_element = card.find('span', string='Attack')
                if attack_element:
                    attack_value = attack_element.find_next('span', class_='border')
                    weapon['attack'] = int(attack_value.text) if attack_value else ''
                
                # Extract technology level
                tech_element = card.find('span', string='Technology')
                if tech_element:
                    tech_value = tech_element.find_next('span', class_='border')
                    weapon['technology'] = int(tech_value.text) if tech_value else ''
                
                # Extract ammo type
                ammo_element = card.find('span', string='Ammo')
                if ammo_element:
                    ammo_value = ammo_element.find_next('span', class_='border')
                    weapon['ammo'] = ammo_value.text if ammo_value else ''
                
                # Extract description
                desc_element = card.find('div', class_='card-body')
                weapon['description'] = desc_element.text.strip() if desc_element else ''
                
                # Extract weapon image URL
                weapon['image'] = f"../assets/images/items/{weapon['name'].replace(" ","-").lower()}.png"
                
                img_element = card.find('img', loading='lazy')
                weapon['image_url'] = img_element['src'] if img_element else ''
                
                # Extract recipe items
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    
                    weapon['recipe'] = recipe_items
                    
                sts=self.stats(weapon['name'].replace(' ', '_'),weapon['rarity'])
                if sts:
                    weapon['stats'] = sts
                
                weapons.append(weapon)
            with open(f"weapon.json", "w") as f:
                json.dump(weapons, f, indent=2)  
            
        return weapons

    def get_sphere(self):
        """Retrieve detailed information about all spheres."""
        url = 'https://paldb.cc/en/Sphere'
        soup = self.get_soup(url)
        spheres = []
        
        if soup:
            sphere_cards = soup.find_all('div', class_='card itemPopup')
            counter = 0
            for card in sphere_cards:
                sphere = {}
                
                counter += 1
                sphere['ID'] = counter
                # Check if sphere is available
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                                
                # Extract sphere name
                name_element = card.find('a', class_='itemname')
                sphere['name'] = name_element.text.strip() if name_element else ''
                
                # Extract sphere rarity
                for i in range(5):  # 0-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        sphere['rarity'] = rarity_element.text.strip()
                        break
                
                # Extract capture power
                power_element = card.find('span', string='Capture Power')
                if power_element:
                    power_value = power_element.find_next('span', class_='border')
                    sphere['capture_power'] = int(power_value.text) if power_value else ''
                
                # Extract technology level
                tech_element = card.find('span', string='Technology')
                if tech_element:
                    tech_value = tech_element.find_next('span', class_='border')
                    sphere['technology'] = int(tech_value.text) if tech_value else ''
                
                # Extract description
                desc_element = card.find('div', class_='card-body')
                sphere['description'] = desc_element.text.strip() if desc_element else ''
                
                
                # Extract sphere image URL
                sphere['image'] = f"../../assets/images/item/{sphere['name'].replace(" ","-").lower()}.png"
                
                img_element = card.find('img', loading='lazy')
                sphere['image_url'] = img_element['src'] if img_element else ''
               
                
                # Extract recipe items
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    
                    sphere['recipe'] = recipe_items
                
                sts=self.stats(sphere['name'].replace(' ', '_'),sphere['rarity'])
                if sts:
                    sphere['stats'] = sts
                spheres.append(sphere)
                
            # Save to JSON file
            with open("spheres.json", "w") as f:
                json.dump(spheres, f, indent=2)
                
        return spheres

    def get_sphere_module(self):
        """Retrieve detailed information about all sphere modules."""
        url = 'https://paldb.cc/en/Sphere_Module'
        soup = self.get_soup(url)
        modules = []
        
        if soup:
            module_cards = soup.find_all('div', class_='card itemPopup')
            counter = 0
            for card in module_cards:
                module = {}
                
                # Check if sphere is available
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                
                counter += 1
                module['ID'] = counter
                # Extract module name
                name_element = card.find('a', class_='itemname')
                module['name'] = name_element.text.strip() if name_element else ''
                
                # Extract module rarity
                for i in range(1, 5):  # 1-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'text-center hover_text_rarity{i}')
                    if rarity_element:
                        module['rarity'] = rarity_element.text.strip()
                        break
                
                # Extract technology level
                tech_element = card.find('span', string='Technology')
                if tech_element:
                    tech_value = tech_element.find_next('span', class_='border')
                    module['technology'] = int(tech_value.text) if tech_value else ''
                
                # Extract description and effects
                desc_element = card.find('div', class_='card-body')
                if desc_element:
                    module['description'] = desc_element.text.split('div>')[0].strip()
                    effects = desc_element.find_all('div', class_='item_skill_bar')
                    module['effects'] = [effect.text.strip() for effect in effects]
                
                
                # Extract module image URL
                img_element = card.find('img', loading='lazy')
                module['image'] = f"../assets/images/items/{module['name'].replace(" ","-").lower()}.png"
                module['image_url'] = img_element['src'] if img_element else ''
                
                # Extract recipe items
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    
                    module['recipe'] = recipe_items
                sts=self.stats(module['name'].replace(' ', '_'),module['rarity'])
                if sts:
                    module['stats'] = sts
                modules.append(module)
                
            # Save to JSON file
            with open("inventory/sphere_modules.json", "w") as f:
                json.dump(modules, f, indent=2)
                
        return modules

    def get_armor(self):
        """Retrieve detailed information about all armor."""
        url = 'https://paldb.cc/en/Armor'
        soup = self.get_soup(url)
        armors = []
        
        if soup:
            armor_cards = soup.find_all('div', class_='card itemPopup')
            counter = 0
            for card in armor_cards:
                armor = {}
                
                
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                counter += 1
                armor['ID'] = counter
                # Extract armor name
                name_element = card.find('a', class_='itemname')
                armor['name'] = name_element.text.strip() if name_element else ''
                print(name_element.text.strip())
                # Extract armor rarity
                for i in range(5):  # 0-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        armor['rarity'] = rarity_element.text.strip()
                        break
                
                # Extract defense value
                defense_element = card.find('span', string='Defense')
                if defense_element:
                    defense_value = defense_element.find_next('span', class_='border')
                    armor['defense'] = int(defense_value.text) if defense_value else ''
                
                # Extract health value
                health_element = card.find('span', string='Health')
                if health_element:
                    health_value = health_element.find_next('span', class_='border')
                    armor['health'] =int( health_value.text) if health_value else ''
                
                # Extract technology level
                tech_element = card.find('span', string='Technology')
                if tech_element:
                    tech_value = tech_element.find_next('span', class_='border')
                    armor['technology'] = int(tech_value.text) if tech_value else ''
                
                # Extract description and effects
                desc_element = card.find('div', class_='card-body')
                if desc_element:
                    armor['description'] = desc_element.text.split('div>')[0].strip()
                    effects = desc_element.find_all('div', class_='item_skill_bar')
                    armor['effects'] = [effect.text.strip() for effect in effects]
                
                
                # Extract armor image URL
                img_element = card.find('img', loading='lazy')
                armor['image'] = f"../assets/images/items/{armor['name'].replace(" ","-").lower()}.png"
                armor['image_url'] = img_element['src'] if img_element else ''
                with sync_playwright() as p:
                    browser = p.firefox.launch()
                    page = browser.new_page()
                    image_url = img_element['src']
                    page.goto(image_url)
                    
                    # Assuming the image URL is directly accessible
                    name = armor['name'].replace(" ","-").lower()
                    download_image(image_url,name )
                
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    
                    armor['recipe'] = recipe_items
                sts=self.stats(armor['name'].replace(' ', '_'),armor['rarity'])
                if sts:
                    armor['stats'] = sts
                    
                armors.append(armor)
                
            # Save to JSON file
            with open("armors.json", "w") as f:
                json.dump(armors, f, indent=2)
                
        return armors

    def get_accessory(self):
        """Retrieve detailed information about all accessories."""
        url = 'https://paldb.cc/en/Accessory'
        soup = self.get_soup(url)
        accessories = []
        
        if soup:
            accessory_cards = soup.find_all('div', class_='card itemPopup')
            count = 0
            for card in accessory_cards:
                accessory = {}
                
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                count += 1
                accessory['id'] = count
                # Extract accessory name
                name_element = card.find('a', class_='itemname')
                accessory['name'] = name_element.text.strip() if name_element else ''
                
                # Extract accessory rarity
                for i in range(5):  # 0-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        accessory['rarity'] = rarity_element.text.strip()
                        break
                
                # Extract description and effects
                desc_element = card.find('div', class_='card-body')
                if desc_element:
                    # Get main description
                    description_text = desc_element.text.split('div>')[0].strip()
                    accessory['description'] = description_text
                    
                    # Get effects/skills
                    effects = desc_element.find_all('div', class_='item_skill_bar')
                    accessory['effects'] = [effect.text.strip() for effect in effects]
                
                
                # Extract accessory image URL
                img_element = card.find('img', loading='lazy')
                accessory['image'] = f"../assets/images/items/{accessory['name'].replace(" ","-").lower()}.png"
                accessory['image_url'] = img_element['src'] if img_element else ''
                with sync_playwright() as p:
                    browser = p.firefox.launch()
                    page = browser.new_page()
                    image_url = img_element['src']
                    page.goto(image_url)
                    
                    # Assuming the image URL is directly accessible
                    name = accessory['name'].replace(" ","-").lower()
                    download_image(image_url,name )
                
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    
                sts = self.stats(accessory['name'].replace(' ', '_'),accessory['rarity'])
                if sts:
                    accessory['stats'] = sts
                
                accessories.append(accessory)
                
            # Save to JSON file
            with open("inventory/accessories.json", "w") as f:
                json.dump(accessories, f, indent=2)
                
        return accessories

    def get_material(self):
        """Retrieve detailed information about all materials."""
        url = 'https://paldb.cc/en/Material'
        soup = self.get_soup(url)
        materials = []
        
        if soup:
            material_cards = soup.find_all('div', class_='card itemPopup')
            
            counter = 0
            for card in material_cards:
                material = {}
                not_available = card.find('i', class_='fa-solid fa-sack-xmark text-danger')
                if not_available:
                    continue
                counter += 1
                material['id'] = counter
                # Extract material name
                name_element = card.find('a', class_='itemname')
                material['name'] = name_element.text.strip() if name_element else ''
                
                # Extract material rarity
                for i in range(5):  # 0-4 for different rarity levels
                    rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
                    if rarity_element:
                        material['rarity'] = rarity_element.text.strip()
                        break
                
                # Extract technology level if exists
                tech_element = card.find('span', string='Technology')
                if tech_element:
                    tech_value = tech_element.find_next('span', class_='border')
                    material['technology'] = int(tech_value.text) if tech_value else ''
                
       
                # Extract description
                desc_element = card.find('div', class_='card-body')
                material['description'] = desc_element.text.strip() if desc_element else ''
                
                # Extract image URL
                img_element = card.find('div', class_='d-flex h-100').find('img')
                material['image'] = f"../assets/images/items/{material['name'].replace(" ","-").lower()}.png"
                material['image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else ''
                # with sync_playwright() as p:
                #     browser = p.firefox.launch()
                #     page = browser.new_page()
                #     image_url = img_element['src']
                #     page.goto(image_url)
                    
                #     # Assuming the image URL is directly accessible
                #     name = material['name'].replace(" ","-").lower()
                    # download_image(image_url,name )
                
                recipe_div = card.find('div', class_='recipes')
                if recipe_div:
                    recipe_items = []
                    recipe_rows = recipe_div.find_all('div', class_='d-flex justify-content-between p-2 align-items-center border-top')
                    
                    for row in recipe_rows:
                        item = {}
                        item_name = row.find('a', class_='itemname')
                        item_quantity = row.find_all('div')[1]
                        item_img = row.find('img', loading='lazy')
                        
                        item['name'] = item_name.text if item_name else ''
                        item['quantity'] = int(item_quantity.text) if item_quantity else ''
                        item['image'] = f"../assets/images/items/{item_name.text.replace(" ","-").lower()}.png" if item_img else ''
                        item['image_url'] = item_img['src'] if item_img else ''
                        recipe_items.append(item)
                    material['recipe'] = recipe_items
                sts = self.stats(material['name'].replace(' ', '_'),material['rarity'])
                if sts:
                    material['stats'] = sts
                
                
                materials.append(material)
                       
            # Save to JSON file
            with open("materials.json", "w") as f:
                json.dump(materials, f, indent=2)
                
        return materials

pal_details = PalDetails()
acc = pal_details.get_material()
