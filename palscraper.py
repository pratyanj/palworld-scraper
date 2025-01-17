import os
import re
import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import argparse

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

    def fetch_url(self, url, timeout=10):
        """Fetch a URL with retry logic and return the response."""
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
        if response:
            return BeautifulSoup(response.text, 'html.parser')
        return None

    def clean_image_url(self, image_url):
        """Clean and return a simplified image URL."""
        return re.sub(r'/revision/.*', "", image_url) if image_url else None

    def download_image(self, image_url, pal_name):
        """Download an image to a local directory."""
        download_path = os.path.join(os.getcwd(), "images", f"{pal_name}.png")
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        response = self.fetch_url(image_url)
        if response:
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"Image downloaded successfully to: {download_path}")

    def parse_work_suitability(self, soup):
        """Extract work suitability information."""
        work_elements = soup.select('div.pi-smart-data-value b')
        suitability = []
        for work in work_elements:
            text = work.text.lower()
            work_type = ''.join(c for c in text if not c.isdigit()).strip()
            level = int(''.join(filter(str.isdigit, text))) if any(c.isdigit() for c in text) else 1
            suitability.append({
                "type": work_type,
                "image": f"../assets/images/works/{work_type}.png",
                "level": level
            })
        return suitability

    def parse_drops(self, soup):
        """Extract drop items."""
        drops = []
        drop_section = soup.find('div', {'data-source': 'drops'})
        if drop_section:
            for span in drop_section.select('.pi-data-value span'):
                name = span.find_all('a')[-1] if span.find_all('a') else None
                if name:
                    drops.append({
                        "name": name.get_text(strip=True),
                        "image": f"../assets/images/items/{name.get_text(strip=True)}"
                    })
        return drops

    def parse_partner_skill(self, soup):
        """Extract partner skill information."""
        skill_name = soup.select_one('div[data-source="partnerskill"] .pi-data-value.pi-font')
        skill_desc = soup.select_one('div[data-source="psdesc"]')

        return {
            "name": skill_name.text.strip() if skill_name else None,
            "description": ''.join(skill_desc.stripped_strings) if skill_desc else None
        }

    def get_pal_details(self, pal_name):
        """Retrieve detailed information about a Pal."""
        url = f'https://palworld.fandom.com/wiki/{pal_name}'
        soup = self.get_soup(url)
        if not soup:
            return None

        pal_number = soup.select_one('div[data-source="no"] .pi-data-value')
        pal_description = soup.select_one('div.decktext')
        small_image = soup.select_one('div.deckentrytitle img')
        full_image = soup.select_one('a.image.image-thumbnail img')

        data = {
            "Key": pal_number.text.strip() if pal_number else "Unknown",
            "name": pal_name,
            "small_image": self.clean_image_url(small_image['data-src']) if small_image else None,
            "full_image": self.clean_image_url(full_image['src']) if full_image else None,
            "description": pal_description.text.strip() if pal_description else "No description available",
            "food": len(soup.select('div.pi-data-value.pi-font img:not(.wsgray)')),
            "work_suitability": self.parse_work_suitability(soup),
            "drops": self.parse_drops(soup),
            "partner_skill": self.parse_partner_skill(soup)
        }

        return data

    def stats(self, pal_name):
        """Retrieve stats and active skills for a Pal."""
        url = f'https://paldb.cc/en/{pal_name}'
        soup = self.get_soup(url)
        if not soup:
            return None

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
                        print(f"Skipping {name} as it already exists with value: {stats[name]}")
                else:
                    stats[name] = value
            except Exception as e:
                print(f"Error processing stat row: {e}")
                continue

        active_skills = []
        skills_section = soup.find('h5', text='Active Skills')
        if skills_section:
            for card in skills_section.parent.parent.select('div.card.itemPopup'):
                try:
                    skill_header = card.select_one('div.align-self-center').text.strip()
                    level = re.search(r'Lv\. (\d+)', skill_header).group(1)
                    skill_name = card.select_one('a').text.strip()
                    stats_div = card.select_one('div.d-flex.pt-1.px-3')
                    active_skills.append({
                        "level": level,
                        "name": skill_name,
                        "element": stats_div.select_one('span').text.strip() if stats_div else None,
                        "cooldown": stats_div.select_one('span[style="color: #73ffff"]').text.strip() if stats_div else None,
                        "power": stats_div.select_one('div.ps-3:last-child span').text.strip() if stats_div else None,
                        "description": card.select_one('div.card-body').text.strip()
                    })
                except Exception as e:
                    print(f"Error processing skill card: {e}")
                    continue

        return {
            "stats": stats,
            "active_skills": active_skills
        }


def get_pal_name():
    import customtkinter as ctk

    # Create the main window but hide it
    root = ctk.CTk()
    root.geometry("550x800")
    root.withdraw()
    
    # Ask for pal name using a dialog box
    dialog = ctk.CTkInputDialog(title="Input", text="Enter Pal Name:")
    pal_name = dialog.get_input()
    
    # Destroy the main window
    root.destroy()
    
    return pal_name
# Get pal name using dialog
pal_name = get_pal_name()
if pal_name:
    pal_scraper = PalDetails()
    print(f"Fetching details for pal: {pal_name}")
    pal_details = pal_scraper.get_pal_details(pal_name)
    pal_stats = pal_scraper.stats(pal_name)
    if pal_details:
        data = pal_details, pal_stats
        import json
        with open(f"{pal_name}.json", "w") as f:
            json.dump(data, f, indent=2)

