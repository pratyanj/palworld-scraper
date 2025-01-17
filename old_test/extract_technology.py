from bs4 import BeautifulSoup
import json
import re
import requests

def extract_technology_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    technologies = []
    
    # Get Technology Points
    tech_points = soup.find('span', text='Technology Points')
    tech_points_value = tech_points.find_next('span', class_='border').text if tech_points else None
    
    # Extract each technology card
    tech_cards = soup.find_all('div', class_='hoverTech')
    
    for index, card in enumerate(tech_cards, 1):
        tech = {}
        
        # Extract ID (from position)
        tech['id'] = index
        
        # Extract name from footer
        footer = card.find('div', class_='hoverTechFooter')
        tech['name'] = footer.text.strip() if footer else ''
        
        # Extract type from header
        header = card.find('div', class_='hoverTechHeader')
        tech['type'] = header.text.strip() if header else ''
        
        # Extract image URL from style attribute
        style = card.get('style', '')
        img_url = re.search(r'url\((.*?)\)', style)
        tech['img_url'] = img_url.group(1) if img_url else ''
        
        # Extract image filename from URL
        tech['img'] = tech['img_url'].split('/')[-1] if tech['img_url'] else ''
        
        # Add Technology Points
        tech['technology_points'] = tech_points_value
        
        # Add Technology level (from parent div)
        level_div = card.find_parent('div', class_='col')
        if level_div:
            level_number = level_div.find('div', style=True)
            tech['technology'] = level_number.text if level_number else ''
        
        technologies.append(tech)
    
    return technologies

def save_to_json(data, filename='technology.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # Read HTML file
    url = 'https://paldb.cc/en/Technology'
    response = requests.get(url)
    html_content = response.text
    
    # Extract data
    tech_data = extract_technology_data(html_content)
    
    # Save to JSON
    save_to_json(tech_data)
    print(f"Extracted {len(tech_data)} technologies to technology.json")

if __name__ == "__main__":
    main()
