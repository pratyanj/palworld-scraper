import os
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from playwright.sync_api import sync_playwright
from PIL import Image

def download_image(image_url, save_path):
    download_path = os.path.join(os.getcwd(), "images", f"{save_path}.png")
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

        self.base_dir = os.getcwd()
        self.image_dir = os.path.join(self.base_dir, "images")
        self.inventory_dir = os.path.join(self.base_dir, "inventory")
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.inventory_dir, exist_ok=True)

    def fetch_url(self, url, timeout=120):
        """Fetch a URL with retry logic and return the response."""
        headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 6.3; Win 64 ; x64) Apple WeKit /537.36(KHTML , like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    }

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch URL {url}: {e}")
            return None

    def get_soup(self, url):
        """Retrieve and parse the HTML content of a given URL."""
        response = self.fetch_url(url)
        return BeautifulSoup(response.text, 'html.parser') if response else None
    
    def playwrite(self,url:str,name:str):
        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            image_url = url
            page.goto(image_url)
            
            # Assuming the image URL is directly accessible
            nameX = name.replace(" ","-").lower()
            download_image(image_url,nameX )

    def extract_item_details(self, card, item_type,id,img:bool):
        """Extract details common to all items."""
        item = {}

        # Check availability
        if card.find('i', class_='fa-solid fa-sack-xmark text-danger'):
            return None
        # ID
        item['id'] = id
        total_items = id
        # Name
        name_element = card.find('a', class_='itemname')
        item['name'] = name_element.text.strip() if name_element else ''
        print('--------------------------------------------------------------------------')
        print("Name:", item['name'])
        # Rarity
        
        for i in range(5):
            rarity_element = card.find('span', class_=f'hover_text_rarity{i}')
            if rarity_element:
                item['rarity'] = rarity_element.text.strip()
                print("Rarity:", item['rarity'])
                break
        if not rarity_element:
            item['rarity'] = 'Common'
            print("Rarity: Common")
        

        # Description
        desc_element = card.find('div', class_='card-body')
        item['description'] = desc_element.text.strip() if desc_element else ''
        print("Description:", item['description'])
        # Image
        img_element = card.find('img', loading='lazy')
        image_name = item['name'].replace(" ", "-").lower()
        # item['image'] = f"../assets/images/{item_type}/{image_name}.png"
        item['image_url'] = img_element['src'] if img_element else ''
        print("Image URL:", item['image_url'])
        if item['image_url']:
            if img:
                self.playwrite(item['image_url'], image_name)
            else:
                pass
                

        # Recipe
        recipe_div = card.find('div', class_='recipes')
        if recipe_div:
            recipe_items = []
            recipe_rows = recipe_div.find_all(
                'div', class_='d-flex justify-content-between p-2 align-items-center border-top'
            )
            for row in recipe_rows:
                recipe_item = {}
                item_name = row.find('a', class_='itemname')
                item_quantity = row.find_all('div')[1]
                recipe_img = row.find('img', loading='lazy')

                recipe_item['name'] = item_name.text.strip() if item_name else ''
                recipe_item['quantity'] = int(item_quantity.text) if item_quantity else ''
                # recipe_item['image'] = f"../assets/images/items/{recipe_item['name'].replace(' ', '-').lower()}.png"
                recipe_item['image_url'] = recipe_img['src'] if recipe_img else ''
                recipe_items.append(recipe_item)
            item['recipe'] = recipe_items
        print("Recipe:", item['recipe'])
       
        sts = self.stats(item['name'].replace(' ', '_'),page=item_type,rarity=item['rarity'])
            
        if sts:
            item['stats'] = sts
        return item

    def stats(self, item_name: str, page: str, rarity: str = "Common"):
        try:
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
            print(f"Item Name: {item_name}")
            if "Shield" in item_name:
                stat_rows = soup.find("div.card-body div.d-flex.justify-content-between.p-2")
            elif page in ['weapons', 'armors']:
                if rarity == "Common":
                    stat_rows = soup.find("div#Items div.card-body div.d-flex.justify-content-between.p-2")
                elif rarity == "Uncommon":
                    stat_rows = soup.select( "div#Items-1 div.card-body div.d-flex.justify-content-between.p-2")
                elif rarity == "Rare":
                    stat_rows = soup.select("div#Items-2 div.card-body div.d-flex.justify-content-between.p-2")
                elif rarity == "Epic":
                    stat_rows = soup.select("div#Items-3 div.card-body div.d-flex.justify-content-between.p-2")
                elif rarity == "Legendary":
                    stat_rows = soup.select("div#Items-4 div.card-body div.d-flex.justify-content-between.p-2")
                
            # Get all stat rows from the card
            
            else:  
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
                    else:
                        stats[name] = value
                        
                except Exception as e:
                    print(f"Error processing stat row: {e}")
                    continue
            # print(f"Stats: {stats}")
            with open("stats.json", "w") as f:
                    json.dump(stats, f, indent=2)
            return stats
        except Exception as e:
            print(f"Warning: Could not collect stats for {item_name}: {e}")
            return {}
    def process_items(self, url, item_type, filename,img ,additional_processing=None,):
        """Generic method to process items and save details to a file."""
        soup = self.get_soup(url)
        items = []
        if soup:
            item_cards = soup.find_all('div', class_='card itemPopup')
            count = 0 
            for card in item_cards:
                count += 1
                item = self.extract_item_details(card, item_type,count,img)
                if item and additional_processing:
                    additional_processing(card, item)
                if item:
                    items.append(item)

            # Save to JSON
            file_path = os.path.join(self.inventory_dir, filename)
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2)
            print(f"Data saved to {file_path}")

        return items

    def get_weapon(self,img):
        """Retrieve weapon details."""
        def process_weapon(card, weapon):
            # Additional weapon-specific processing
            attack_element = card.find('span', string='Attack')
            if attack_element:
                attack_value = attack_element.find_next('span', class_='border')
                weapon['attack'] = int(attack_value.text) if attack_value else ''
            # Technology
            tech_element = card.find('span', string='Technology')
            if tech_element:
                tech_value = tech_element.find_next('span', class_='border')
                weapon['technology'] = int(tech_value.text) if tech_value else ''
            # Extract ammo type
            ammo_element = card.find('span', string='Ammo')
            if ammo_element:
                ammo_value = ammo_element.find_next('span', class_='border')
                weapon['ammo'] = ammo_value.text if ammo_value else ''

        return self.process_items('https://paldb.cc/en/Weapon', 'weapons', 'weapons.json',img,process_weapon)

    def get_sphere(self,img):
        """Retrieve sphere details."""
        def process_sphere(card, sphere):
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
        return self.process_items('https://paldb.cc/en/Sphere', 'spheres', 'spheres.json',img,process_sphere)

    def get_sphere_module(self,img):
        """Retrieve sphere module details."""
        def process_sphere_module(card, sphere_module):
            # Extract technology level
            tech_element = card.find('span', string='Technology')
            if tech_element:
                tech_value = tech_element.find_next('span', class_='border')
                sphere_module['technology'] = int(tech_value.text) if tech_value else ''
        return self.process_items('https://paldb.cc/en/Sphere_Module', 'sphere_modules', 'sphere_modules.json',img ,process_sphere_module)

    def get_armor(self,img):
        """Retrieve armor details."""
        def process_armor(card, armor):
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
            
            # Extract sheild value
            shield_element = card.find('span', string='Shield')
            if shield_element:
                shield_value = shield_element.find_next('span', class_='border')
                armor['shield'] = int(shield_value.text) if shield_value else ''
            
        return self.process_items('https://paldb.cc/en/Armor', 'armors', 'armors.json',img,process_armor)

    def get_accessory(self,img):
        """Retrieve accessory details."""
        def process_accessory(card, accessory):
        # Extract description and effects
            desc_element = card.find('div', class_='card-body')
            if desc_element:
                # Get main description
                description_text = desc_element.text.split('div>')[0].strip()
                accessory['description'] = description_text
                
                # Get effects/skills
                effects = desc_element.find_all('div', class_='item_skill_bar')
                accessory['effects'] = [effect.text.strip() for effect in effects]
        return self.process_items('https://paldb.cc/en/Accessory', 'accessories', 'accessories.json',img,process_accessory)

    def get_Consumable(self,img):
            """Retrieve consumable details.""" 
            def process_Consumable(card, consumable):
                # Extract Nutrition value
                Nutrition_element = card.find('span', string='Nutrition')
                if Nutrition_element:
                    Nutrition_value = Nutrition_element.find_next('span', class_='border')
                    consumable['Nutrition'] =int( Nutrition_value.text) if Nutrition_value else ''
                
                # Extract SAN value
                SAN_element = card.find('span', string='SAN')
                if SAN_element:
                    SAN_value = SAN_element.find_next('span', class_='border')
                    consumable['san'] =int( SAN_value.text) if SAN_value else ''

                # Extract Work Speed value
                Work_Speed_element = card.find('span', string='Work Speed')
                if Work_Speed_element:
                    Work_Speed_value = Work_Speed_element.find_next('span', class_='border')
                    consumable['stamina_work'] =int( Work_Speed_value.text) if Work_Speed_value else ''

                # Extract SANResist value
                SANResist_element = card.find('span', string='SANResist')
                if SANResist_element:
                    SANResist_value = SANResist_element.find_next('span', class_='border')
                    consumable['san_resist'] =int( SANResist_value.text) if SANResist_value else ''
                
                # Extract Recovery Time value
                Recovery_Time_element = card.find('span', string='Recovery Time')
                if Recovery_Time_element:
                    Recovery_Time_value = Recovery_Time_element.find_next('span', class_='border')
                    consumable['recovery_time'] =int( Recovery_Time_value.text) if Recovery_Time_value else ''

                # Extract Technology Points value
                Technology_Points_element = card.find('span', string='Technology Points')
                if Technology_Points_element:
                    Technology_Points_value = Technology_Points_element.find_next('span', class_='border')
                    consumable['technology_points'] =int( Technology_Points_value.text) if Technology_Points_value else ''
                    
                # Extract Technology value
                Technology_element = card.find('span', string='Technology')
                if Technology_element:
                    Technology_value = Technology_element.find_next('span', class_='border')
                    consumable['technology'] =int( Technology_value.text) if Technology_value else ''
                    
                # Extract MaxHP value
                MaxHP_element = card.find('span', string='MaxHP')
                if MaxHP_element:
                    MaxHP_value = MaxHP_element.find_next('span', class_='border')
                    consumable['max_hp'] =int( MaxHP_value.text) if MaxHP_value else ''
                
                # Extract MaxSP value
                MaxSP_element = card.find('span', string='MaxSP')
                if MaxSP_element:
                    MaxSP_value = MaxSP_element.find_next('span', class_='border')
                    consumable['max_sp'] =int( MaxSP_value.text) if MaxSP_value else ''
                # Extract Power value
                Power_element = card.find('span', string='Power')
                if Power_element:
                    Power_value = Power_element.find_next('span', class_='border')
                    consumable['power'] =int( Power_value.text) if Power_value else ''
                # Extract MaxInventoryWeight value
                MaxInventoryWeight_element = card.find('span', string='MaxInventoryWeight')
                if MaxInventoryWeight_element:
                    MaxInventoryWeight_value = MaxInventoryWeight_element.find_next('span', class_='border')
                    consumable['max_inventory_weight'] =int( MaxInventoryWeight_value.text) if MaxInventoryWeight_value else ''

                # Extract Exp value
                Exp_element = card.find('span', string='Exp')
                if Exp_element:
                    Exp_value = Exp_element.find_next('span', class_='border')
                    consumable['exp'] =int( Exp_value.text) if Exp_value else ''
                
            return self.process_items('https://paldb.cc/en/Consumable', 'consumables', 'consumables.json',img,process_Consumable)
    
    def get_ammo(self,img):
        def process_ammo(card, ammo):
            
            # Extract Ammo Type value
            Technology_element = card.find('span', string='Technology')
            if Technology_element:
                Technology_value = Technology_element.find_next('span', class_='border')
                ammo['technology'] =int( Technology_value.text) if Technology_value else ''
                
        return (self.process_items('https://paldb.cc/en/Ammo', 'ammo', 'ammo.json',img, process_ammo))
    
    def get_Ingredient(self,img):
        def process_Ingredient(card, ingredient):

            # Extract Nutrition value
            Nutrition_element = card.find('span', string='Nutrition')
            if Nutrition_element:
                Nutrition_value = Nutrition_element.find_next('span', class_='border')
                ingredient['Nutrition'] =int( Nutrition_value.text) if Nutrition_value else ''
                
            # Extract SAN value
            SAN_element = card.find('span', string='SAN')
            if SAN_element:
                SAN_value = SAN_element.find_next('span', class_='border')
                ingredient['SAN'] =int( SAN_value.text) if SAN_value else ''
            
            # Extract Work Speed value
            Work_Speed_element = card.find('span', string='Work Speed')
            if Work_Speed_element:
                Work_Speed_value = Work_Speed_element.find_next('span', class_='border')
                ingredient['Work Speed'] =int( Work_Speed_value.text) if Work_Speed_value else ''
                
            # Extract Recovery Time value
            Recovery_Time_element = card.find('span', string='Recovery Time')
            if Recovery_Time_element:
                Recovery_Time_value = Recovery_Time_element.find_next('span', class_='border')
                ingredient['Recovery Time'] =int( Recovery_Time_value.text) if Recovery_Time_value else ''
            
            # Extract Defense value
            Defense_element = card.find('span', string='Defense')
            if Defense_element:
                Defense_value = Defense_element.find_next('span', class_='border')
                ingredient['Defense'] =int( Defense_value.text) if Defense_value else ''

            # Extract SANResist value
            SANResist_element = card.find('span', string='SANResist')
            if SANResist_element:
                SANResist_value = SANResist_element.find_next('span', class_='border')
                ingredient['SANResist'] =int( SANResist_value.text) if SANResist_value else ''
            
            # Extract Attack value
            Attack_element = card.find('span', string='Attack')
            if Attack_element:
                Attack_value = Attack_element.find_next('span', class_='border')
                ingredient['Attack'] =int( Attack_value.text) if Attack_value else ''

            # Extract HungerResist value
            HungerResist_element = card.find('span', string='HungerResist')
            if HungerResist_element:
                HungerResist_value = HungerResist_element.find_next('span', class_='border')
                ingredient['HungerResist'] =int( HungerResist_value.text) if HungerResist_value else ''
                 
        return (self.process_items('https://paldb.cc/en/Ingredient', 'ingredients', 'ingredients.json',img, process_Ingredient))

    # ------------------------construction---------------------------
    def get_Production(self,img):
        # Extract SAN value
        def process_Production(card, production):
            # Extract SAN value
            SAN_element = card.find('span', string='SAN')
            if SAN_element:
                SAN_value = SAN_element.find_next('span', class_='border')
                production['SAN'] =SAN_value.text if SAN_value else ''
            
            # Extract Ammo Type value
            Technology_element = card.find('span', string='Technology')
            if Technology_element:
                Technology_value = Technology_element.find_next('span', class_='border')
                production['technology'] =int( Technology_value.text) if Technology_value else ''
        
        return self.process_items('https://paldb.cc/en/Production', 'productions', 'productions.json',img,process_Production)
# Create GUI for data collection


