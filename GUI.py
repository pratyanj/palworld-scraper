import customtkinter as ctk
import threading
from tkinter import messagebox
import pandas as pd
from main import PalDetails
import json

class PalWorldGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("PalWorld Data Collector")
        self.window.geometry("800x700")
        
        self.img_select = False
        
        # Set theme and colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create TabView
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        # Create tabs
        self.tab1 = self.tabview.add("Data Collector")
        self.tab2 = self.tabview.add("Custom Extractor")

        # Tab 1 - Original Content
        self.setup_collector_tab()

        # Tab 2 - Custom Extractor
        self.setup_extractor_tab()

    def setup_collector_tab(self):
        # Move original container content here
        self.container = ctk.CTkFrame(self.tab1)
        self.container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Header section
        self.header_frame = ctk.CTkFrame(self.container)
        self.header_frame.pack(pady=10, padx=10, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="PalWorld Data Collector",
            font=("Roboto", 24, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Progress section
        self.progress_frame = ctk.CTkFrame(self.container)
        self.progress_frame.pack(pady=10, padx=10, fill="x")
        
        self.progress = ctk.CTkProgressBar(self.progress_frame, height=15)
        self.progress.pack(pady=10, fill="x", padx=20)
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to collect data",
            font=("Roboto", 12),
            fg_color="#2B2B2B",
            corner_radius=8,
            
        )
        self.status_label.pack(pady=5)
        
        self.checkboxfram = ctk.CTkFrame(self.container)
        self.checkboxfram.pack(pady=10, padx=10, fill="x")

        self.img_label = ctk.CTkLabel(
            self.checkboxfram, 
            text="Do you want image to download?", 
            font=("Roboto", 12)
        )
        self.img_label.pack(side="left", padx=5)

        self.truechcek = ctk.CTkCheckBox(self.checkboxfram, text="Yes", checkbox_height=20, checkbox_width=20)
        self.truechcek.pack(side="left", padx=5)

              
        self.test_label = ctk.CTkLabel(self.checkboxfram, text="Testing data", font=("Roboto", 12))
        self.test_label.pack(side="left", padx=10)
        self.test_true = ctk.CTkCheckBox(self.checkboxfram, text="True", checkbox_height=20, checkbox_width=20)
        self.test_true.pack(side="left", padx=10)
        

        # Buttons section - using grid layout
        self.buttons_frame = ctk.CTkFrame(self.container)
        self.buttons_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.buttons = {
            "Weapons": ("🗡️", self.collect_weapons),
            "Spheres": ("⭕", self.collect_spheres),
            "Sphere Modules": ("🔮", self.collect_sphere_modules),
            "Armor": ("🛡️", self.collect_armor),
            "Accessories": ("💍", self.collect_accessories),
            "Consumables": ("🍖", self.collect_consumables),
            "Ammo": ("🎯", self.collect_ammo),
            "Ingredients": ("🧪", self.collect_ingredients),
            "Productions": ("⚒️", self.collect_productions),
        }
        
        # Create buttons in a grid layout
        row = 0
        col = 0
        for text, (icon, command) in self.buttons.items():
            btn = ctk.CTkButton(
                self.buttons_frame,
                text=f"{icon} {text}",
                command=command,
                width=200,
                height=50,
                font=("Roboto", 14),
                corner_radius=10,
                hover_color="#1f538d"
            )
            btn.grid(row=row, column=col, pady=10, padx=10, sticky="nsew")
            col += 1
            if col > 2:  # 3 buttons per row
                col = 0
                row += 1
                
        # Configure grid weights
        for i in range(3):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
            
        # Footer with stats
        self.footer_frame = ctk.CTkFrame(self.container)
        self.footer_frame.pack(pady=10, padx=10, fill="x")
        
        
        self.stats_label = ctk.CTkLabel(
            self.footer_frame,
            text="Total items collected: 0",
            font=("Roboto", 12),
            
        )
        self.stats_label.pack(pady=5)
        
        self.pal_details = PalDetails()

    def setup_extractor_tab(self):
        extractor_frame = ctk.CTkFrame(self.tab2)
        extractor_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Item Type Dropdown
        self.item_type_label = ctk.CTkLabel(
            extractor_frame,
            text="Select Item Type:",
            font=("Roboto", 14)
        )
        self.item_type_label.pack(pady=10)

        self.item_types = [
            "Weapons",
            "Spheres",
            "Sphere Modules",
            "Armor",
            "Accessories",
            "Consumables",
            "Ammo",
            "Ingredients",
            "Productions"
        ]

        self.item_type_var = ctk.StringVar(value=self.item_types[3])
        self.item_type_dropdown = ctk.CTkOptionMenu(
            extractor_frame,
            values=self.item_types,
            variable=self.item_type_var,
            width=200,
            font=("Roboto", 12)
        )
        self.item_type_dropdown.pack(pady=10)
        
        self.rarity_label = ctk.CTkLabel(
            extractor_frame,
            text="Select Rarity:",
            font=("Roboto", 14)
        )
        self.rarity_label.pack(pady=10)
        
        self.raritys = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        self.rarity_var = ctk.StringVar(value=self.raritys[4])
        self.rarity_dropdown = ctk.CTkOptionMenu(
            extractor_frame,
            values=self.raritys,
            variable=self.rarity_var,
            width=200,
            font=("Roboto", 12)
        )

        self.rarity_dropdown.pack(pady=10)
        # URL Input
        self.url_label = ctk.CTkLabel(
            extractor_frame,
            text="Enter Item name:",
            font=("Roboto", 14)
        )
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(
            extractor_frame,
            width=400,
            placeholder_text="Place item name here",
        )
        self.url_entry.pack(pady=10)


        # Extract Button
        self.extract_button = ctk.CTkButton(
            extractor_frame,
            text="Extract Item",
            command=self.extract_custom_item,
            width=200,
            height=40,
            font=("Roboto", 14),
            corner_radius=10
        )
        self.extract_button.pack(pady=20)

        # Results Display
        self.results_text = ctk.CTkTextbox(
            extractor_frame,
            width=600,
            height=400,
            font=("Roboto", 16)
        )
        self.results_text.pack(pady=10)

    def extract_custom_item(self):
        item_type = self.item_type_var.get()
        name = self.url_entry.get()
        rarity=self.rarity_dropdown.get()

        if not name:
            messagebox.showwarning("Warning", "Please enter a URL")
            return

        try:
            # Here you can implement the custom extraction logic
            # using your existing PalDetails class methods
            self.results_text.delete("1.0", "end")
            data = self.pal_details.stats(name,item_type,rarity)
            self.results_text.insert("1.0", json.dumps(data, indent=4))
            # Add actual extraction logic here
        except Exception as e:
            self.results_text.insert("end", f"Error: {str(e)}\n")
        
    def show_loading(self, is_loading=True):
        if is_loading:
            self.progress.start()
            self.status_label.configure(
                text="Collecting data...",
                fg_color="#c09553"
            )
            for widget in self.buttons_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state="disabled")
        else:
            self.progress.stop()
            self.progress.set(1)
            self.status_label.configure(
                text="✅ complete!",
                fg_color="#2dcc9f"
            )
            for widget in self.buttons_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state="normal")
                    
    def update_stats(self,file_name:str):
        # Update collection statistics
        count = pd.read_json(f'inventory/{file_name}')
        counts = len(count)
        self.stats_label.configure(text=f"Total items collected: {counts}")
        
    def img_check(self):
        if self.truechcek.get():
            return True
        else:
            return False
    def test_check(self):
        if self.test_true.get():
            return True
        else:
            return False
    
    def collect_data(self, collection_function,file_name):
        try:
            self.show_loading(True)
            collection_function()
            self.show_loading(False)
            print(f"Data collected and saved to {file_name}")
            self.update_stats(file_name)
            messagebox.showinfo("Success", "Data collected successfully!")
        except Exception as e:
            self.show_loading(False)
            print(f"An error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Define the collection functions
    def collect_weapons(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_weapon(self.img_check(),self.test_check()),"weapons.json")).start()
    
    def collect_spheres(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_sphere(self.img_check(),self.test_check()),'spheres.json')).start()
    
    def collect_sphere_modules(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_sphere_module(self.img_check(),self.test_check()),'sphere_modules.json')).start()
    
    def collect_armor(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_armor(self.img_check(),self.test_check()),'armors.json')).start()
    
    def collect_accessories(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_accessory(self.img_check(),self.test_check()),'accessories.json')).start()
        
    def collect_consumables(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Consumable(self.img_check(),self.test_check()),'consumables.json')).start()
    
    def collect_ammo(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_ammo(self.img_check(),self.test_check()),'ammo.json')).start()
        
    def collect_ingredients(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Ingredient(self.img_check(),self.test_check()),'ingredients.json')).start()
        
    def collect_productions(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Production(self.img_check(),self.test_check()),'productions.json')).start()
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PalWorldGUI()
    app.run()