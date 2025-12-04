import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import xmlrpc.client
import base64
import io
from PIL import Image, ImageTk # C'est ici qu'on utilise Pillow
 
class OdooProductShop:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Stock Odoo")
        self.root.geometry("800x500")
 
        # Config Odoo (Mets tes infos ici)
        self.url = "http://localhost:8069"
        self.db = "demo"      # Ton nom de base
        self.username = "bouin.loig@gmail.com"
        self.password = "MSIR5"
        self.uid = None
        self.models = None
        self.products_data = {} # Pour stocker temporairement les infos
 
        self.setup_ui()
        self.connect_and_load()
 
    def setup_ui(self):
        # --- Zone Gauche : Liste des produits ---
        self.frame_list = tk.Frame(self.root, width=250, bg="#e1e1e1")
        self.frame_list.pack(side="left", fill="y")
 
        self.lbl_list = tk.Label(self.frame_list, text="Mes Produits", bg="#e1e1e1", font=("Arial", 12, "bold"))
        self.lbl_list.pack(pady=10)
 
        self.listbox = Listbox(self.frame_list, width=30)
        self.listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_product) # Événement clic
 
        # --- Zone Droite : Détails ---
        self.frame_detail = tk.Frame(self.root, bg="white")
        self.frame_detail.pack(side="right", fill="both", expand=True)
 
        self.lbl_title = tk.Label(self.frame_detail, text="Sélectionnez un produit", font=("Arial", 18, "bold"), bg="white")
        self.lbl_title.pack(pady=20)
 
        # Placeholder pour l'image
        self.lbl_image = tk.Label(self.frame_detail, bg="white")
        self.lbl_image.pack(pady=10)
 
        self.lbl_price = tk.Label(self.frame_detail, text="", font=("Arial", 14), bg="white")
        self.lbl_price.pack(pady=5)
 
        self.lbl_stock = tk.Label(self.frame_detail, text="", font=("Arial", 14), fg="blue", bg="white")
        self.lbl_stock.pack(pady=5)
 
    def connect_and_load(self):
        try:
            # 1. Connexion
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                messagebox.showerror("Erreur", "Connexion refusée")
                return
 
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            self.load_products()
 
        except Exception as e:
            messagebox.showerror("Erreur Connection", str(e))
 
    def load_products(self):
        try:
            # 2. Récupération des produits
            # On demande l'image en petite taille (image_128) pour aller plus vite
            fields = ['name', 'list_price', 'qty_available', 'image_1920'] 
            # On cherche tous les produits (domain=[])
            products = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'search_read',
                [[]], 
                {'fields': fields, 'limit': 20} # Limite à 20 pour le test
            )
 
            # On remplit la Listbox
            for prod in products:
                # On stocke l'objet complet dans un dico avec l'index de la liste comme clé
                index = self.listbox.size()
                self.listbox.insert(index, prod['name'])
                self.products_data[index] = prod
 
        except Exception as e:
            messagebox.showerror("Erreur Lecture", str(e))
 
    def on_select_product(self, event):
        # Récupération de l'index cliqué
        selection = self.listbox.curselection()
        if not selection:
            return
 
        index = selection[0]
        data = self.products_data[index]
 
        # Mise à jour des textes
        self.lbl_title.config(text=data['name'])
        self.lbl_price.config(text=f"Prix : {data['list_price']} €")
        self.lbl_stock.config(text=f"En stock : {data['qty_available']} unités")
 
        # Mise à jour de l'image
        self.display_image(data.get('image_1920'))
 
    def display_image(self, base64_string):
        if not base64_string:
            self.lbl_image.config(image='', text="(Pas d'image)")
            return
 
        try:
            # 1. Décodage du Base64 (Texte -> Binaire)
            img_data = base64.b64decode(base64_string)
            # 2. Ouverture avec Pillow (Binaire -> Image Object)
            img = Image.open(io.BytesIO(img_data))
            # 3. Redimensionnement pour que ça rentre dans l'écran
            img.thumbnail((250, 250)) 
            # 4. Conversion pour Tkinter
            tk_image = ImageTk.PhotoImage(img)
            # 5. Affichage
            self.lbl_image.config(image=tk_image, text="")
            self.lbl_image.image = tk_image # Important : garder une référence sinon le Garbage Collector l'efface !
        except Exception as e:
            print(f"Erreur image: {e}")
            self.lbl_image.config(image='', text="(Erreur chargement image)")
 
if __name__ == "__main__":
    root = tk.Tk()
    app = OdooProductShop(root)
    root.mainloop()