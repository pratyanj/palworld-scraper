import requests
from bs4 import BeautifulSoup
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lxml import etree 
import requests 
import os

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
    
    def get_active_skills(self, soup):
        skills = []
        skill_rows = soup.select('tbody tr:nth-of-type(odd)')
        description_rows = soup.select('tbody tr:nth-of-type(even)')

        for skill_row, desc_row in zip(skill_rows, description_rows):
            try:
                level = skill_row.select_one('th b').text.replace('Lv ', '') if skill_row.select_one('th b') else None
                skill_name = skill_row.select_one('td b a').text if skill_row.select_one('td b a') else None
                skill_icon = skill_row.select_one('td a img')
                skill_icon = self.clean_image_url(skill_icon['data-src']) if skill_icon else None
                cooldown = skill_row.select_one('td:nth-of-type(2)').text.replace('CT: ', '').strip() if skill_row.select_one('td:nth-of-type(2)') else None
                power = skill_row.select_one('td:nth-of-type(3)').text.replace('Power: ', '').strip() if skill_row.select_one('td:nth-of-type(3)') else None
                description = desc_row.select_one('td').text.strip() if desc_row.select_one('td') else None

                if level and skill_name:  # Only add valid skills
                    skills.append({
                        "level": level,
                        "name": skill_name,
                        "icon": skill_icon,
                        "cooldown": cooldown,
                        "power": power,
                        "description": description
                    })
            except Exception as e:
                print(f"Error processing skill: {e}")
                continue
        
        return skills
        
    def download_image(self, image_url, pal_name):
        download_path = os.path.join(os.getcwd(), "images", f"{pal_name}.png")
        os.makedirs(os.path.join(os.getcwd(), "images"), exist_ok=True)        
        response = self.session.get(image_url)
        if response.status_code == 200:
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"Image downloaded successfully to: {download_path}")
    def clean_image_url(self, image_url):
        if image_url:
            # print(f"Cleaning image URL: {image_url}")
            return re.sub(r'/revision/.*', "", image_url)
        # print("No image URL to clean.")
        return image_url

    def get_pal_details(self, pal_name):
        url = f'https://palworld.fandom.com/wiki/{pal_name}'
        print(f"Fetching URL: {url}")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch details for {pal_name}: {e}")
            return None

        if response.status_code != 200:
            print(f"Failed to retrieve data for {pal_name}, HTTP {response.status_code}")
            return None

        # print("Successfully fetched the page content.")
        soup = BeautifulSoup(response.text, 'html.parser')
        dom = etree.HTML(str(soup)) 
        # Basic Info
        
        pal_number = soup.select_one('div[data-source="no"] .pi-data-value').text.strip() if soup.select_one('div[data-source="no"] .pi-data-value') else "Unknown"
        # print(f"Pal Number: {pal_number}")
        
        # pal_name = soup.select_one('div.deckentrytitle').text.strip() if soup.select_one('div.deckentrytitle') else "Unknown"
        # print(f"Pal Name: {pal_name}")
        pal_small_image = soup.select_one('div.deckentrytitle img')['data-src']
        pal_small_image = self.clean_image_url(pal_small_image)
        # self.download_image(pal_small_image, (pal_name+" Profile"))
        # print(f"Pal small Image: {pal_small_image}")
        
        try:
            pal_full_image = soup.select_one('a.image.image-thumbnail img')
        except: 
            pal_full_image = soup.select_one('img.image.image-thumbnail')
        pal_full_image = pal_full_image['src'] if pal_full_image else None
        # self.download_image(pal_full_image, (pal_name+" Full"))
        
        
        # print(f"Pal Full Image: {pal_full_image}")
        pal_description = soup.select_one('div.decktext').text.strip() if soup.select_one('div.decktext') else "No description available"
        # print(f"Pal Description: {pal_description}")

        # Work Suitability
        # Work Suitability
        work_elements = soup.select('div.pi-smart-data-value b')
        pal_work_suitability = []
        for work in work_elements:
            work_type = ''.join(c for c in work.text.lower() if not c.isdigit()).strip()
            level = int(''.join(filter(str.isdigit, work.text))) if any(char.isdigit() for char in work.text) else 1            
            pal_work_suitability.append({
                "type": work_type,
                "image": f"../assets/images/works/{work_type}.png",
                "level": level
            })

        print(f"Work Suitability: {pal_work_suitability}")
        
        
        # Food Rating
        food_section = len(dom.xpath('//div[@class="pi-data-value pi-font"]/img[not(contains(@class, "wsgray"))]'))
        # print(f"Food Section: {food_section}")
        
        
        # Stats
        # Stats section url:
        # https://palworld.gg/pal/astegon
        # stats = {}
        # # Get all stat rows (skip header row by starting from position 2)
        # stat_rows = dom.xpath('//table[contains(@class, "wikitable")]/tbody/tr[position()>1 and position()<5]')
        # # Debug prints
        # # print("Found stat rows:", len(stat_rows))
        # count = 0
        # for row in stat_rows:
        #     try:
        #         columns = row.xpath('./td')
        #         if len(columns) >= 5:  # Only process rows with enough columns
        #             name = row.xpath('string(./td[1])').strip()
        #             # Filter out unwanted rows
        #             if name in ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]:
        #                 # print(f"Processing stat row {count}: {name}")
        #                 base = columns[1].xpath('./text()')[0].strip()
        #                 # print(f"Base: {base}")
        #                 min_val = columns[3].xpath('./text()')[0].strip()
        #                 # print(f"Min Level 55: {min_val}")
        #                 max_val = columns[4].xpath('./text()')[0].strip()
        #                 # print(f"Max Level 55: {max_val}")
                        
        #                 stats[name] = {
        #                     "base": base,
        #                     "min_level_55": min_val,
        #                     "max_level_55": max_val
        #                 }
        #                 count += 1  # Increment count only for valid rows
        #     except Exception as e:
        #         print(f"Error processing stat row: {e}")

        # print(f"Stats: {stats}")
        
        # Drop Items
        drops = []
        drop_section = soup.find('div', {'data-source': 'drops'})
        
        if drop_section:
            # Find all span elements containing item info
            for span in drop_section.select('.pi-data-value span'):
                # Get image element
                img = span.find('img')
                # Get name element (second anchor tag)
                name = span.find_all('a')[-1] if span.find_all('a') else None
                
                if img and name:
                    drops.append({
                        "name": name.get_text(strip=True),
                        "image": img.get('data-src')
                    })
        # print(f"Pal drops:{drops}")    
        
        # Partner Skill
        partner_skill_name = soup.select_one('div[data-source="partnerskill"] .pi-data-value.pi-font')
        partner_skill_name = partner_skill_name.text.strip() if partner_skill_name else None
        # print(f"Partner Skill Name: {partner_skill_name}")

        partner_skill_img = soup.select_one('div[data-source="psicon"] img')
        partner_skill_img = self.clean_image_url(partner_skill_img['data-src']) if partner_skill_img else None
        # print(f"Partner Skill Icon: {partner_skill_img}")

        partner_skill_description = soup.select_one('div[data-source="psdesc"]')
        partner_skill_description = ''.join(partner_skill_description.stripped_strings) if partner_skill_description else None
        # print(f"Partner Skill Description: {partner_skill_description}")

        partner_skill = {
            "name": partner_skill_name,
            "icon": partner_skill_img,
            "description": partner_skill_description
        }
        # print(f"Partner Skill: {partner_skill}")
        # Active Skills
    
         
        data ={
            "Key":pal_number,
            "name": pal_name,
            "small_image": pal_small_image,
            "full_image": pal_full_image,
            "description": pal_description,
            "food": food_section,
            "work_suitability": pal_work_suitability,
            "drops": drops,
            "partner_skill": partner_skill,
        }
        # print(f"Data: {data}")
        return data

    def stats(self,pal_name):
        url = f'https://paldb.cc/en/{pal_name}'
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch details for {pal_name}: {e}")
            return None

        if response.status_code != 200:
            print(f"Failed to retrieve data for {pal_name}, HTTP {response.status_code}")
            return None

        # print("Successfully fetched the page content.")
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(f"Soup: {soup}")
        stats = {}
        # Get all stat rows from the card
        stat_rows = soup.select('div.card-body div.d-flex.justify-content-between.p-2')

        for row in stat_rows:
            try:
                # Get the stat name and value
                name = row.select_one('div:first-child').text.strip()
                value = row.select_one('div:last-child').text.strip()
                
                # Check if the name is in the desired keys
                if name in ['MeleeAttack', 'Attack', 'Defense', 'Health']:
                    # Only add if the key is not already in stats
                    if name not in stats:
                        print(f"{name} : {value}")
                        stats[name] = value
                    
                else:
                    
                    stats[name] = value
            except Exception as e:
                print(f"Error processing stat row: {e}")
                continue
        # print(f"Stats: {stats}")
        movement_stats = {}
    # Find the movement stats card
        movement_card = soup.find('h5', string='Movement').parent.parent
        if movement_card:
            stat_rows = movement_card.select('div.d-flex.justify-content-between.p-2')
            for row in stat_rows:
                name = row.select_one('div:first-child').text.strip()
                value = row.select_one('div:last-child').text.strip()
                movement_stats[name] = value
        
        other_details = {}
        others_card = soup.find('h5', string=' Others ').parent.parent
        if others_card:
            detail_rows = others_card.select('div.d-flex.justify-content-between.p-2')
            for row in detail_rows:
                name = row.select_one('div:first-child').text.strip()
                value = row.select_one('div:last-child').text.strip()
                other_details[name] = value
        
        active_skills = []
        # Find the Active Skills card
        # skills_section = soup.find('h5', text='Active Skills').parent.parent
        skills_section = soup.find('h5', string='Active Skills').parent.parent

        if skills_section:
            skill_cards = skills_section.select('div.card.itemPopup')
            for card in skill_cards:
                try:
                    # Extract level and name
                    skill_header = card.select_one('div.align-self-center').text.strip()
                    level = skill_header.split('Lv. ')[1].split()[0]
                    skill_name = card.select_one('a').text.strip()
                    
                    # Extract element, cooldown and power
                    stats_div = card.select_one('div.d-flex.pt-1.px-3')
                    element = stats_div.select_one('span').text.strip() if stats_div else None
                    cooldown = stats_div.select_one('span[style="color: #73ffff"]').text.strip() if stats_div else None
                    power = stats_div.select_one('div.ps-3:last-child span').text.strip() if stats_div else None
                    
                    # Extract description
                    description = card.select_one('div.card-body').text.strip()
                    
                    active_skills.append({
                        "level": level,
                        "name": skill_name,
                        "element": element,
                        "cooldown": cooldown,
                        "power": power,
                        "description": description
                    })
                except Exception as e:
                    print(f"Error processing skill card: {e}")
                    continue
                    
        return [stats,movement_stats,other_details,active_skills]
        
        
        
# Example Usage
pal_scraper = PalDetails()
pal_name = "Dazemu"
print(f"Fetching details for pal: {pal_name}")
# pal_details = pal_scraper.get_pal_details(pal_name)
pal_details = pal_scraper.stats(pal_name)
if pal_details:
    print("Retrieved Pal Details:")
    print(pal_details)
else:
    print("Failed to retrieve pal details.")