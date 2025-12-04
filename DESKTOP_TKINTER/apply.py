import tkinter as tk
from tkinter import messagebox, Listbox
import xmlrpc.client
import base64
import io
from PIL import Image, ImageTk
 
# --- CONSTANTES DE CONFIGURATION ---
URL = "http://localhost:8069"
DB = "demo"
 
class OdooApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mon App Odoo Modulaire")
        self.geometry("900x600")
        # Données de session partagées
        self.uid = None
        self.password = None
        self.username = None
        self.models = None # Le proxy pour les objets
        # Conteneur principal qui empile les vues
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
 
        self.frames = {}
        # On déclare toutes nos vues ici pour les instancier au démarrage
        for F in (LoginView, MenuView, CompanyView, ProductView):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # On les met toutes au même endroit (pile)
            frame.grid(row=0, column=0, sticky="nsew")
 
        self.show_frame("LoginView")
 
    def show_frame(self, page_name):
        '''Monte une vue au premier plan'''
        frame = self.frames[page_name]
        frame.tkraise()
        # Si la vue a une méthode de rafraichissement, on l'appelle
        if hasattr(frame, "on_show"):
            frame.on_show()
 
    def connect_odoo(self, username, password):
        '''Méthode centrale de connexion appelée par LoginView'''
        try:
            common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
            uid = common.authenticate(DB, username, password, {})
            if uid:
                self.uid = uid
                self.username = username
                self.password = password
                self.models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
                return True
            return False
        except Exception as e:
            messagebox.showerror("Erreur Réseau", str(e))
            return False
 
# --- VUE 1 : LOGIN ---
class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Design centré
        box = tk.Frame(self, padx=20, pady=20, relief="raised", borderwidth=2)
        box.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(box, text="Connexion Odoo", font=("Arial", 16)).pack(pady=10)
 
        tk.Label(box, text="Utilisateur").pack(anchor="w")
        self.entry_user = tk.Entry(box); self.entry_user.insert(0, "bouin.loig@gmail.com"); self.entry_user.pack(fill="x")
 
        tk.Label(box, text="Mot de passe").pack(anchor="w", pady=(5,0))
        self.entry_pass = tk.Entry(box, show="*"); self.entry_pass.insert(0, "MSIR5"); self.entry_pass.pack(fill="x")
 
        tk.Button(box, text="Se connecter", command=self.attempt_login, bg="#008787", fg="white").pack(pady=20, fill="x")
 
    def attempt_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if self.controller.connect_odoo(user, pwd):
            self.controller.show_frame("MenuView")
        else:
            messagebox.showerror("Erreur", "Login incorrect")
 
# --- VUE 2 : MENU PRINCIPAL (TILES) ---
class MenuView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Tableau de Bord", font=("Arial", 20)).pack(pady=30)
        tile_frame = tk.Frame(self)
        tile_frame.pack(expand=True)
 
        # Création des Tiles (Boutons carrés)
        self.create_tile(tile_frame, "🏢\nMon Entreprise", "CompanyView", 0, 0)
        self.create_tile(tile_frame, "📦\nMes Produits", "ProductView", 0, 1)
        # Future tile : self.create_tile(tile_frame, "Factures", "InvoiceView", 0, 2)
        tk.Button(self, text="Déconnexion", command=lambda: controller.show_frame("LoginView")).pack(pady=20)
 
    def create_tile(self, parent, text, view_name, r, c):
        btn = tk.Button(parent, text=text, font=("Arial", 14), width=15, height=5,
                        command=lambda: self.controller.show_frame(view_name),
                        relief="groove", bg="#f0f0f0")
        btn.grid(row=r, column=c, padx=20, pady=20)
 
# --- VUE 3 : FICHE ENTREPRISE ---
class CompanyView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Header avec bouton retour
        header = tk.Frame(self, bg="#ddd", height=40)
        header.pack(fill="x")
        tk.Button(header, text="< Menu", command=lambda: controller.show_frame("MenuView")).pack(side="left", padx=5, pady=5)
        tk.Label(header, text="Informations Société", bg="#ddd").pack(side="left", padx=10)
 
        # Contenu
        self.lbl_info = tk.Label(self, text="Chargement...", font=("Arial", 12), justify="left")
        self.lbl_info.pack(pady=50)
 
    def on_show(self):
        # Cette fonction se lance à chaque fois qu'on affiche la vue
        try:
            uid = self.controller.uid
            pwd = self.controller.password
            models = self.controller.models
            data = models.execute_kw(DB, uid, pwd, 'res.company', 'search_read', 
                                   [[]], {'fields': ['name', 'email', 'phone', 'vat'], 'limit': 1})
            if data:
                c = data[0]
                text = f"Nom : {c['name']}\nEmail : {c['email']}\nTéléphone : {c['phone']}\nTVA : {c['vat']}"
                self.lbl_info.config(text=text)
        except Exception as e:
            self.lbl_info.config(text=f"Erreur : {e}")
 
# --- VUE 4 : PRODUITS (SHOP) ---
class ProductView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Header
        header = tk.Frame(self, bg="#ddd")
        header.pack(fill="x")
        tk.Button(header, text="< Menu", command=lambda: controller.show_frame("MenuView")).pack(side="left", padx=5, pady=5)
        # Layout Gauche/Droite
        content = tk.Frame(self)
        content.pack(fill="both", expand=True)
        # Liste
        self.listbox = Listbox(content, width=30)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind('<<ListboxSelect>>', self.load_detail)
        # Détail
        self.detail_frame = tk.Frame(content, padx=20)
        self.detail_frame.pack(side="right", fill="both", expand=True)
        self.lbl_name = tk.Label(self.detail_frame, text="", font=("Arial", 16, "bold"))
        self.lbl_name.pack(pady=10)
        self.lbl_img = tk.Label(self.detail_frame)
        self.lbl_img.pack()
        self.lbl_price = tk.Label(self.detail_frame, text="")
        self.lbl_price.pack()
 
        self.products_map = {} # Cache local
 
    def on_show(self):
        # Recharger la liste quand on arrive sur la page
        self.listbox.delete(0, tk.END)
        self.products_map = {}
        try:
            models = self.controller.models
            products = models.execute_kw(DB, self.controller.uid, self.controller.password,
                'product.product', 'search_read', [[]], 
                {'fields': ['name', 'list_price', 'image_1920'], 'limit': 20})
 
            for p in products:
                idx = self.listbox.size()
                self.listbox.insert(idx, p['name'])
                self.products_map[idx] = p
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
 
    def load_detail(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        data = self.products_map[sel[0]]
        self.lbl_name.config(text=data['name'])
        self.lbl_price.config(text=f"{data['list_price']} €")
        # Gestion Image
        img_b64 = data.get('image_1920')
        if img_b64:
            img_data = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_data))
            img.thumbnail((200, 200))
            tk_img = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=tk_img)
            self.lbl_img.image = tk_img
        else:
            self.lbl_img.config(image='', text="Pas d'image")
 
if __name__ == "__main__":
    app = OdooApp()
    app.mainloop()