import tkinter as tk
from tkinter import messagebox, Listbox
import base64
import io
from PIL import Image, ImageTk
 
# On importe notre backend
from odoo_api import OdooClient
 
# --- CONFIGURATION DU THÈME SOMBRE ---
THEME = {
    "bg_main": "#FFFFFF",       # Fond principal
    "bg_sec":  "#B3B3B3",       # Fond secondaire (cartes, listes)
    "fg_text": "#1B1B1B",       # Texte principal
    "fg_sub":  "#1DAB5A",       # Texte accentué (Cyan)
    "btn_bg":  "#29F180",       # Boutons
    "btn_fg":  "#2D2D2D",       # Texte boutons
    "entry_bg": "#222831",      # Fond des champs texte
    "entry_fg": "#FFFFFF"       # Texte des champs
}
 
class ModernOdooApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Odoo Dark Manager")
        self.geometry("900x600")
        self.configure(bg=THEME["bg_main"])
 
        # --- POINT CRITIQUE 1 : La Racine ---
        # On dit à la fenêtre principale : "La cellule (0,0) doit prendre 100% de la place disponible"
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
 
        # Instanciation de l'API
        self.api = OdooClient("http://localhost:8069", "demo")
 
        # --- POINT CRITIQUE 2 : Le Conteneur ---
        self.container = tk.Frame(self, bg=THEME["bg_main"])
        # sticky="nsew" force le cadre à coller aux 4 bords (North, South, East, West)
        self.container.grid(row=0, column=0, sticky="nsew")
        # On dit au conteneur : "La vue qui est dedans doit aussi prendre 100% de la place"
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
 
        self.frames = {}
        # Création des vues
        # Assure-toi que ManufacturingView est bien dans la liste !
        for F in (LoginView, MenuView, CompanyView, ProductView, ManufacturingView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # --- POINT CRITIQUE 3 : Les Vues ---
            # Chaque vue doit s'étirer pour remplir le conteneur
            frame.grid(row=0, column=0, sticky="nsew")
 
        self.show_frame("LoginView")
 
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()
 
# --- CLASSE UTILITAIRE POUR LE STYLE ---
class DarkFrame(tk.Frame):
    """Un Frame pré-configuré avec le thème sombre"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=THEME["bg_main"], **kwargs)
 
# --- VUE 1 : LOGIN ---
class LoginView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        box = tk.Frame(self, bg=THEME["bg_sec"], padx=40, pady=40)
        box.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(box, text="CONNEXION", font=("Segoe UI", 18, "bold"), 
                 bg=THEME["bg_sec"], fg=THEME["fg_text"]).pack(pady=20)
 
        self.entry_user = self.create_input(box, "prod")
        self.entry_pass = self.create_input(box, "prod", is_pass=True)
 
        btn = tk.Button(box, text="ACCÉDER", command=self.attempt_login,
                        bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Arial", 10, "bold"),
                        activebackground=THEME["fg_sub"], relief="flat", padx=20, pady=10)
        btn.pack(pady=20, fill="x")
 
    def create_input(self, parent, default, is_pass=False):
        e = tk.Entry(parent, bg=THEME["entry_bg"], fg=THEME["entry_fg"], 
                     insertbackground="white", relief="flat", font=("Arial", 12))
        e.insert(0, default)
        if is_pass: e.config(show="*")
        e.pack(pady=10, ipady=5, fill="x")
        return e
 
    def attempt_login(self):
        if self.controller.api.login(self.entry_user.get(), self.entry_pass.get()):
            self.controller.show_frame("MenuView")
        else:
            messagebox.showerror("Erreur", "Login ou mot de passe incorrect")
 
# --- VUE 2 : MENU ---
class MenuView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="TABLEAU DE BORD", font=("Segoe UI", 24), 
                 bg=THEME["bg_main"], fg=THEME["fg_sub"]).pack(pady=50)
        tile_area = tk.Frame(self, bg=THEME["bg_main"])
        tile_area.pack()
 
        self.create_tile(tile_area, "🏢 SOCIÉTÉ", "CompanyView", 0, 0)
        self.create_tile(tile_area, "📦 PRODUITS", "ProductView", 0, 1)
        self.create_tile(tile_area, "🏭 FABRICATION", "ManufacturingView", 1, 0)
        tk.Button(self, text="Déconnexion", command=lambda: controller.show_frame("LoginView"),
                  bg=THEME["bg_sec"], fg="red", relief="flat").pack(pady=50)
 
    def create_tile(self, parent, text, view, r, c):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 14), 
                        bg=THEME["bg_sec"], fg=THEME["fg_text"],
                        activebackground=THEME["fg_sub"], relief="flat",
                        width=15, height=5,
                        command=lambda: self.controller.show_frame(view))
        btn.grid(row=r, column=c, padx=20, pady=20)
 
# --- VUE 3 : SOCIÉTÉ ---
class CompanyView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_header("Informations Société")
        self.lbl_content = tk.Label(self, text="", font=("Arial", 14), justify="left",
                                    bg=THEME["bg_main"], fg=THEME["fg_text"])
        self.lbl_content.pack(pady=50)
 
    def create_header(self, text):
        h = tk.Frame(self, bg=THEME["bg_sec"], height=50)
        h.pack(fill="x")
        tk.Button(h, text="< RETOUR", command=lambda: self.controller.show_frame("MenuView"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], relief="flat").pack(side="left", padx=10, pady=10)
        tk.Label(h, text=text, bg=THEME["bg_sec"], fg=THEME["fg_text"], font=("Arial", 12, "bold")).pack(side="left", padx=20)
 
    def on_show(self):
        data = self.controller.api.get_company_info()
        if data:
            self.lbl_content.config(text=f"Nom : {data.get('name')}\nEmail : {data.get('email')}\nTVA : {data.get('vat')}")
 
# --- VUE 4 : PRODUITS ---
class ProductView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Header
        h = tk.Frame(self, bg=THEME["bg_sec"], height=50)
        h.pack(fill="x")
        tk.Button(h, text="< RETOUR", command=lambda: self.controller.show_frame("MenuView"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], relief="flat").pack(side="left", padx=10, pady=10)
 
        # Corps
        body = tk.Frame(self, bg=THEME["bg_main"])
        body.pack(fill="both", expand=True, padx=20, pady=20)
 
        # Liste
        self.listbox = Listbox(body, width=30, bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                               selectbackground=THEME["fg_sub"], selectforeground=THEME["btn_fg"],
                               relief="flat", highlightthickness=0)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind('<<ListboxSelect>>', self.load_detail)
 
        # Détail
        self.detail_area = tk.Frame(body, bg=THEME["bg_main"], padx=20)
        self.detail_area.pack(side="right", fill="both", expand=True)
        self.lbl_name = tk.Label(self.detail_area, text="", font=("Arial", 20, "bold"), bg=THEME["bg_main"], fg=THEME["fg_sub"])
        self.lbl_name.pack(pady=10)
        self.lbl_img = tk.Label(self.detail_area, bg=THEME["bg_main"])
        self.lbl_img.pack(pady=10)
        self.lbl_price = tk.Label(self.detail_area, text="", font=("Arial", 16), bg=THEME["bg_main"], fg=THEME["fg_text"])
        self.lbl_price.pack()
        self.lbl_qty = tk.Label(self.detail_area, text="", font=("Arial", 14), bg=THEME["bg_main"], fg=THEME["fg_text"])
        self.lbl_qty.pack()
 
        self.products_cache = {}
 
    def on_show(self):
        self.listbox.delete(0, tk.END)
        self.products_cache = {}
        products = self.controller.api.get_products()
        for p in products:
            idx = self.listbox.size()
            self.listbox.insert(idx, p['name'])
            self.products_cache[idx] = p
 
    def load_detail(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        data = self.products_cache[sel[0]]
        self.lbl_name.config(text=data['name'])
        self.lbl_price.config(text=f"{data['list_price']} €")
        self.lbl_qty.config(text=f"En stock : {data['qty_available']}")
        img_b64 = data.get('image_1920')
        if img_b64:
            img_data = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_data))
            img.thumbnail((250, 250))
            tk_img = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=tk_img, text="")
            self.lbl_img.image = tk_img
        else:
            self.lbl_img.config(image="", text="Pas d'image", fg="grey")

# --- VUE 5 : FABRICATION (ÉDITION) ---
class ManufacturingView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # 1. Header
        h = tk.Frame(self, bg=THEME["bg_sec"], height=50)
        h.pack(fill="x")
        tk.Button(h, text="< RETOUR", command=lambda: self.controller.show_frame("MenuView"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], relief="flat").pack(side="left", padx=10, pady=10)
        tk.Label(h, text="Pilotage Fabrication", bg=THEME["bg_sec"], fg=THEME["fg_text"], font=("Arial", 12, "bold")).pack(side="left", padx=20)
 
        # 2. Split Screen (PanedWindow)
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=THEME["bg_main"], sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)
 
        # --- ZONE GAUCHE : LISTE ---
        left_frame = tk.Frame(self.paned, bg=THEME["bg_sec"])

        # === AJOUTER CE BLOC POUR LES FILTRES ===
        filter_frame = tk.Frame(left_frame, bg=THEME["bg_sec"], pady=5)
        filter_frame.pack(fill="x") # En haut de la colonne gauche
 
        self.filter_vars = {} 
        states_to_filter = [("confirmed", "Conf."), ("progress", "En cours"), ("done", "Fait"), ("cancel", "Annulé")]
 
        for tech_name, label in states_to_filter:
            # On coche par défaut confirmed et progress
            is_checked = True if tech_name in ["confirmed", "progress"] else False
            var = tk.BooleanVar(value=is_checked)
            self.filter_vars[tech_name] = var
            # command=self.refresh_list pour recharger dès qu'on clique
            cb = tk.Checkbutton(filter_frame, text=label, variable=var, 
                                bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                                selectcolor=THEME["bg_main"], activebackground=THEME["bg_sec"],
                                activeforeground=THEME["fg_sub"],
                                command=self.refresh_list) 
            cb.pack(side="left", padx=5)
# ========================================

        # Scrollbar
        scrollbar = tk.Scrollbar(left_frame)
        scrollbar.pack(side="right", fill="y")
        self.listbox = Listbox(left_frame, width=40, bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                               font=("Courier", 10), selectbackground=THEME["fg_sub"], 
                               relief="flat", highlightthickness=0, yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.load_detail)
        scrollbar.config(command=self.listbox.yview)
 
        self.paned.add(left_frame, minsize=300)
 
        # --- ZONE DROITE : ACTIONS ---
        self.action_area = tk.Frame(self.paned, bg=THEME["bg_main"], padx=20, pady=20)
        self.paned.add(self.action_area, minsize=300, stretch="always")
 
        # Widgets de la zone de droite (initialement cachés ou vides)
        self.lbl_title = tk.Label(self.action_area, text="", font=("Segoe UI", 18, "bold"), bg=THEME["bg_main"], fg=THEME["fg_sub"])
        self.lbl_title.pack(pady=10)
 
        self.lbl_status = tk.Label(self.action_area, text="", font=("Arial", 12, "italic"), bg=THEME["bg_main"], fg="grey")
        self.lbl_status.pack(pady=5)
 
        # Frame pour la saisie
        self.input_frame = tk.Frame(self.action_area, bg=THEME["bg_main"], pady=20)
        self.input_frame.pack()
 
        tk.Label(self.input_frame, text="Quantité Produite :", bg=THEME["bg_main"], fg=THEME["fg_text"]).grid(row=0, column=0)
        self.entry_qty = tk.Entry(self.input_frame, font=("Arial", 14), width=8, justify="center")
        self.entry_qty.grid(row=0, column=1, padx=10)
        self.lbl_target = tk.Label(self.input_frame, text="/ ???", font=("Arial", 14), bg=THEME["bg_main"], fg=THEME["fg_text"])
        self.lbl_target.grid(row=0, column=2)
 
        # Bouton Valider
        self.btn_save = tk.Button(self.action_area, text="ENREGISTRER PRODUCTION", 
                                  command=self.save_production,
                                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Arial", 12, "bold"), padx=20, pady=10)
        self.btn_save.pack(pady=20)
 
        self.current_order = None # Pour stocker l'objet sélectionné
        self.orders_cache = {}
 
    def on_show(self):
        self.refresh_list()
 
    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.orders_cache = {}
        self.current_order = None
        self.hide_input_area()
 
        # 1. On récupère les filtres actifs
        selected_states = []
        for state_key, var in self.filter_vars.items():
            if var.get():
                selected_states.append(state_key)
        # Petite sécurité : si rien n'est coché, on n'appelle pas l'API
        if not selected_states:
            self.listbox.insert(0, "Aucun filtre sélectionné.")
            return
 
        # 2. Appel API AVEC le paramètre states_filter
        try:
            orders = self.controller.api.get_manufacturing_orders(states_filter=selected_states)
            if not orders:
                self.listbox.insert(0, "Aucun ordre trouvé.")
                return
 
            for order in orders:
                idx = self.listbox.size()
                ref = order['name']
                state = order['state']
                # Rappel : assure-toi d'avoir ajouté 'qty_producing' dans odoo_api.py !
                done = order.get('qty_producing', 0) 
                product = order['product_id'][1]
                line = f"[{state.upper()}] {ref} - {product}"
                self.listbox.insert(idx, line)
                order['qty_producing_current'] = done
                self.orders_cache[idx] = order
        except Exception as e:
            print(f"Erreur refresh : {e}")
            self.listbox.insert(0, "Erreur de chargement")
 
    def load_detail(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        data = self.orders_cache[sel[0]]
        self.current_order = data # Stockage de l'OF en cours
 
        # Mise à jour UI
        self.lbl_title.config(text=f"{data['name']} - {data['product_id'][1]}")
        status_map = {'confirmed': 'Confirmé', 'progress': 'En cours', 'done': 'Terminé', 'cancel': 'Annulé', 'draft': 'Brouillon'}
        state_label = status_map.get(data['state'], data['state'])
        self.lbl_status.config(text=f"État actuel : {state_label}")
        # Logique d'affichage selon l'état
        if data['state'] in ['confirmed', 'progress']:
            self.input_frame.pack()
            self.btn_save.pack(pady=20)
            self.btn_save.config(state="normal", bg=THEME["btn_bg"])
            # Remplissage champs
            self.entry_qty.delete(0, tk.END)
            # On affiche la quantité en cours (qty_producing)
            current_prod = data.get('qty_producing_current', 0)
            self.entry_qty.insert(0, str(current_prod))
            self.lbl_target.config(text=f"/ {data['product_qty']}")
        else:
            # Si c'est déjà fini ou annulé, on empêche la modif
            self.hide_input_area()
            self.lbl_status.config(text=f"Cet ordre est {state_label}. Modification impossible.")
 
    def hide_input_area(self):
        self.input_frame.pack_forget()
        self.btn_save.pack_forget()
 
    def save_production(self):
        if not self.current_order: return
        try:
            new_qty = float(self.entry_qty.get())
            target_qty = self.current_order['product_qty']
            mo_id = self.current_order['id'] # L'ID technique Odoo
            # Appel API
            result = self.controller.api.update_production_qty(mo_id, new_qty, target_qty)
            if result == "DONE":
                messagebox.showinfo("Succès", "Quantité atteinte ! L'OF est passé à 'FAIT'.")
            else:
                messagebox.showinfo("Succès", "Quantité mise à jour. L'OF est 'EN COURS'.")
            # On rafraichit la liste pour voir le nouvel état
            self.refresh_list()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
        except Exception as e:
            messagebox.showerror("Erreur Odoo", str(e))
 
if __name__ == "__main__":
    app = ModernOdooApp()
    app.mainloop()