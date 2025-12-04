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
 
        # Instanciation du backend
        self.api = OdooClient("http://localhost:8069", "demo")
 
        # Conteneur des pages
        self.container = tk.Frame(self, bg=THEME["bg_main"])
        self.container.pack(fill="both", expand=True)
 
        self.frames = {}
        # Création des vues
        for F in (LoginView, MenuView, CompanyView, ProductView, ManufacturingView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
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

# --- VUE 5 : ORDRES DE FABRICATION ---
class ManufacturingView(DarkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Header
        h = tk.Frame(self, bg=THEME["bg_sec"], height=50)
        h.pack(fill="x")
        tk.Button(h, text="< RETOUR", command=lambda: self.controller.show_frame("MenuView"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], relief="flat").pack(side="left", padx=10, pady=10)
        tk.Label(h, text="Ordres de Fabrication", bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                 font=("Arial", 12, "bold")).pack(side="left", padx=20)
 
        # Liste des OF
        self.listbox = Listbox(self, bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                               font=("Courier", 10), # Police à chasse fixe pour aligner un peu mieux
                               selectbackground=THEME["fg_sub"], relief="flat", highlightthickness=0)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)

        # Zone de Filtres
        filter_frame = tk.Frame(self, bg=THEME["bg_main"], pady=10)
        filter_frame.pack(fill="x", padx=20)

        self.filter_vars = {}  # Dictionnaire pour stocker l'état (True/False) de chaque case
        states_to_filter = [
            ("confirmed", "Confirmé"),
            ("progress", "En cours"),
            ("done", "Fait"),
            ("cancel", "Annulé")
        ]
 
        for tech_name, label in states_to_filter:
            # Par défaut, on coche tout sauf "Annulé" et "Fait" pour ne pas polluer (au choix)
            is_checked = True if tech_name in ["confirmed", "progress"] else False
            var = tk.BooleanVar(value=is_checked)
            self.filter_vars[tech_name] = var
            # On crée la checkbox# command=self.on_show -> Dès qu'on clique, ça recharge la liste !
            cb = tk.Checkbutton(filter_frame, text=label, variable=var, 
                                bg=THEME["bg_main"], fg=THEME["fg_text"], 
                                selectcolor=THEME["bg_sec"], activebackground=THEME["bg_main"],
                                activeforeground=THEME["fg_sub"],
                                command=self.on_show) 
            cb.pack(side="left", padx=10)

        # Liste
        self.listbox = Listbox(self, bg=THEME["bg_sec"], fg=THEME["fg_text"], 
                               font=("Courier", 10), selectbackground=THEME["fg_sub"], 
                               relief="flat", highlightthickness=0)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)
 
    def on_show(self):
        self.listbox.delete(0, tk.END)

        # 1. On construit la liste des états cochés
        selected_states = []
        for state_key, var in self.filter_vars.items():
            if var.get(): # Si la case est cochée (True)
                selected_states.append(state_key)
        # Si rien n'est coché, on n'affiche rien (ou tout, selon ta préférence)
        if not selected_states:
            self.listbox.insert(0, "Veuillez sélectionner au moins un statut.")
            return
        # 2. Appel API avec le filtre
        try:
            orders = self.controller.api.get_manufacturing_orders(states_filter=selected_states)

            if not orders:
                self.listbox.insert(0, "Aucun ordre trouvé pour ces filtres.")
                return

            for order in orders:
                # Traitement des données Odoo
                ref = order['name']
                state = order['state']
                qty = order.get('product_qty', 0)
                product_name = order['product_id'][1] if order['product_id'] else "Inconnu"

                line = f"[{state.upper()}] {ref} - {product_name} (Qté: {qty})"
                self.listbox.insert(tk.END, line)

        except Exception as e:
            self.listbox.insert(0, f"Erreur API: {e}")
 
if __name__ == "__main__":
    app = ModernOdooApp()
    app.mainloop()