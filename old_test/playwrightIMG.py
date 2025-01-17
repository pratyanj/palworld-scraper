from playwright.sync_api import sync_playwright
import requests

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

def main():
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        image_url = 'https://cdn.paldb.cc/image/Others/InventoryItemIcon/Texture/T_itemicon_Armor_HeadEquip041.webp'
        page.goto(image_url)
        
        # Assuming the image URL is directly accessible
        download_image(image_url, 'downloaded_image.jpg')
        
        browser.close()

if __name__ == "__main__":
    main()