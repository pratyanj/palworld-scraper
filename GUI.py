import customtkinter as ctk
import threading
from tkinter import messagebox
import pandas as pd
from main import PalDetails

class PalWorldGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("PalWorld Data Collector")
        self.window.geometry("800x700")
        
        self.img_select = False
        
        # Set theme and colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main container with grid layout
        self.container = ctk.CTkFrame(self.window)
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

        self.truechcek = ctk.CTkCheckBox(self.checkboxfram, text="Yes", checkbox_height=20, checkbox_width=20, command=lambda: self.falsechcek.deselect())
        self.truechcek.pack(side="left", padx=5)

        self.falsechcek = ctk.CTkCheckBox(self.checkboxfram, text="No", checkbox_height=20, checkbox_width=20, command=lambda: self.truechcek.deselect())
        self.falsechcek.select()        
        self.falsechcek.pack(side="left", padx=5)
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
    
    def collect_data(self, collection_function,file_name):
        try:
            print('-------1-------')
            self.show_loading(True)
            print('-------2-------')
            collection_function()
            print('-------3-------')
            self.show_loading(False)
            print('-------4-------')
            print(f"Data collected and saved to {file_name}")
            print('-------5-------')
            self.update_stats(file_name)
            print('-------6-------')
            messagebox.showinfo("Success", "Data collected successfully!")
        except Exception as e:
            self.show_loading(False)
            print(f"An error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Define the collection functions
    def collect_weapons(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_weapon(self.img_check()),"weapons.json")).start()
    
    def collect_spheres(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_sphere(self.img_check()),'spheres.json')).start()
    
    def collect_sphere_modules(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_sphere_module(self.img_check()),'sphere_modules.json')).start()
    
    def collect_armor(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_armor(self.img_check()),'armors.json')).start()
    
    def collect_accessories(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_accessory(self.img_check()),'accessories.json')).start()
        
    def collect_consumables(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Consumable(self.img_check()),'consumables.json')).start()
    
    def collect_ammo(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_ammo(self.img_check()),'ammo.json')).start()
        
    def collect_ingredients(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Ingredient(self.img_check()),'ingredients.json')).start()
        
    def collect_productions(self):
        threading.Thread(target=lambda: self.collect_data(lambda:self.pal_details.get_Production(self.img_check()),'productions.json')).start()
        
    def run(self):
        self.window.mainloop()
if __name__ == "__main__":
    app = PalWorldGUI()
    app.run()