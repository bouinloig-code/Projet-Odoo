import customtkinter as ctk
from tkinter import messagebox
import base64
import io
from PIL import Image
import threading

# Import backend
from odoo_api import OdooClient

# Configuration globale
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernOdooApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Odoo Manager NextGen")
        self.geometry("1100x700")
        
        # Grid layout 1x1
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Adaptez les identifiants ici si besoin
        self.api = OdooClient("http://localhost:8069", "demo")
        
        # Conteneur principal
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # On charge toutes les vues
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
            # Threading pour ne pas geler l'interface pendant le chargement
            threading.Thread(target=frame.on_show, daemon=True).start()

# --- VUE 1 : LOGIN ---
class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.card = ctk.CTkFrame(self, corner_radius=15)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.card, text="ODOO ACCESS", font=("Roboto Medium", 24)).pack(pady=(40, 20), padx=40)

        self.user_entry = ctk.CTkEntry(self.card, placeholder_text="Utilisateur", width=250)
        self.user_entry.pack(pady=10)
        # Valeurs par défaut pour tester vite
        self.user_entry.insert(0, "admin")

        self.pass_entry = ctk.CTkEntry(self.card, placeholder_text="Mot de passe", show="*", width=250)
        self.pass_entry.pack(pady=10)
        self.pass_entry.insert(0, "admin")

        self.btn_login = ctk.CTkButton(self.card, text="Se connecter", command=self.login_trigger, width=250)
        self.btn_login.pack(pady=(20, 40))

    def login_trigger(self):
        self.btn_login.configure(state="disabled", text="Connexion...")
        threading.Thread(target=self._run_login, daemon=True).start()

    def _run_login(self):
        success = self.controller.api.login(self.user_entry.get(), self.pass_entry.get())
        self.after(0, lambda: self._post_login(success))

    def _post_login(self, success):
        self.btn_login.configure(state="normal", text="Se connecter")
        if success:
            self.controller.show_frame("MenuView")
        else:
            messagebox.showerror("Erreur", "Identifiants invalides")

# --- VUE 2 : MENU ---
class MenuView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Sidebar gauche
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="MENU", font=("Roboto Medium", 20)).pack(pady=30)
        
        ctk.CTkButton(self.sidebar, text="Déconnexion", fg_color="transparent", border_width=2,
                      command=lambda: controller.show_frame("LoginView")).pack(side="bottom", pady=20, padx=20)

        # Zone centrale (Tiles)
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Les Tuiles
        self.create_tile("🏢 Société", "CompanyView", 0, 0)
        self.create_tile("📦 Produits", "ProductView", 0, 1)
        self.create_tile("🏭 Fabrication", "ManufacturingView", 1, 0)

    def create_tile(self, text, view, r, c):
        btn = ctk.CTkButton(self.main_area, text=text, font=("Arial", 18), height=150, width=200,
                            command=lambda: self.controller.show_frame(view))
        btn.grid(row=r, column=c, padx=20, pady=20)

# --- VUE 3 : SOCIÉTÉ (Avec Logo et Adresse) ---
class CompanyView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="< Retour", width=100, fg_color="transparent", border_width=1,
                      command=lambda: controller.show_frame("MenuView")).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(self.header, text="MA SOCIÉTÉ", font=("Roboto", 16)).pack(side="left", padx=20)

        # Contenu principal centré
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        # --- Zone Gauche : Logo ---
        self.logo_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.logo_frame.pack(side="left", padx=40, pady=20)
        
        self.lbl_logo = ctk.CTkLabel(self.logo_frame, text="", width=200, height=200)
        self.lbl_logo.pack()

        # --- Zone Droite : Infos ---
        self.info_frame = ctk.CTkFrame(self.content, width=400) # Cadre visible pour les infos
        self.info_frame.pack(side="left", padx=40, pady=20, fill="y")

        # Nom de l'entreprise
        self.lbl_name = ctk.CTkLabel(self.info_frame, text="Chargement...", font=("Roboto Medium", 26))
        self.lbl_name.pack(pady=(30, 10), padx=20, anchor="w")

        # Adresse (multiligne)
        self.lbl_address = ctk.CTkLabel(self.info_frame, text="", font=("Roboto", 14), justify="left", text_color="grey")
        self.lbl_address.pack(pady=(0, 20), padx=20, anchor="w")

        # Séparateur
        ctk.CTkFrame(self.info_frame, height=2, fg_color="grey").pack(fill="x", padx=20, pady=10)

        # Détails techniques
        self.lbl_email = self.create_row(self.info_frame, "Email :")
        self.lbl_phone = self.create_row(self.info_frame, "Tél :")
        self.lbl_vat = self.create_row(self.info_frame, "TVA :")
        
        # Padding bas
        ctk.CTkLabel(self.info_frame, text="").pack(pady=10)

    def create_row(self, parent, label):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text=label, width=80, anchor="w", font=("Roboto", 14, "bold")).pack(side="left")
        val = ctk.CTkLabel(row, text="...", font=("Roboto", 14))
        val.pack(side="left", padx=10)
        return val

    def on_show(self):
        data = self.controller.api.get_company_info()
        self.after(0, lambda: self.update_view(data))

    def update_view(self, data):
        if not data: return

        # 1. Textes de base
        self.lbl_name.configure(text=data.get('name', 'Inconnu'))
        self.lbl_email.configure(text=data.get('email') or 'N/A')
        self.lbl_phone.configure(text=data.get('phone') or 'N/A')
        self.lbl_vat.configure(text=data.get('vat') or 'N/A')

        # 2. Construction de l'adresse
        rue = data.get('street') or ""
        code = data.get('zip') or ""
        ville = data.get('city') or ""
        adresse_complete = f"{rue}\n{code} {ville}".strip()
        self.lbl_address.configure(text=adresse_complete if adresse_complete else "Adresse non définie")

        # 3. Gestion du Logo
        logo_b64 = data.get('logo')
        if logo_b64:
            try:
                img_data = base64.b64decode(logo_b64)
                pil_img = Image.open(io.BytesIO(img_data))
                
                # On redimensionne proprement
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 180))
                self.lbl_logo.configure(image=ctk_img, text="")
            except Exception as e:
                print(f"Erreur Logo: {e}")
                self.lbl_logo.configure(text="[Erreur Logo]")
        else:
            self.lbl_logo.configure(image=None, text="[Pas de logo]")
            
# --- VUE 4 : PRODUITS (Avec Stock) ---
class ProductView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="< Retour", width=100, fg_color="transparent", border_width=1,
                      command=lambda: controller.show_frame("MenuView")).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(self.header, text="CATALOGUE PRODUITS", font=("Roboto", 16)).pack(side="left", padx=20)

        # Split Screen
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)

        # Liste scrollable
        self.scroll_list = ctk.CTkScrollableFrame(self.content, width=300, label_text="Produits")
        self.scroll_list.pack(side="left", fill="y", padx=(0, 10))

        # Détail
        self.detail_frame = ctk.CTkFrame(self.content)
        self.detail_frame.pack(side="right", fill="both", expand=True)

        self.lbl_name = ctk.CTkLabel(self.detail_frame, text="", font=("Roboto Medium", 24))
        self.lbl_name.pack(pady=20)
        
        self.img_label = ctk.CTkLabel(self.detail_frame, text="")
        self.img_label.pack(pady=10)
        
        self.lbl_price = ctk.CTkLabel(self.detail_frame, text="", font=("Roboto", 20), text_color="#2CC985")
        self.lbl_price.pack(pady=5)

        # AJOUT DU STOCK ICI
        self.lbl_stock = ctk.CTkLabel(self.detail_frame, text="", font=("Roboto", 16), text_color="#3B8ED0")
        self.lbl_stock.pack(pady=5)

        self.products_data = []

    def on_show(self):
        products = self.controller.api.get_products()
        self.products_data = products
        self.after(0, self.update_list)

    def update_list(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        for p in self.products_data:
            btn = ctk.CTkButton(self.scroll_list, text=f"{p['name']}", 
                                fg_color="transparent", border_width=1,
                                command=lambda x=p: self.load_detail(x))
            btn.pack(fill="x", pady=2)

    def load_detail(self, data):
        self.lbl_name.configure(text=data['name'])
        self.lbl_price.configure(text=f"Prix : {data['list_price']} €")
        
        # Mise à jour du stock
        qty = data.get('qty_available', 0)
        self.lbl_stock.configure(text=f"Stock disponible : {qty} unités")
        
        if data.get('image_1920'):
            try:
                img_data = base64.b64decode(data['image_1920'])
                pil_img = Image.open(io.BytesIO(img_data))
                my_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(200, 200))
                self.img_label.configure(image=my_image, text="")
            except:
                self.img_label.configure(image=None, text="Erreur image")
        else:
            self.img_label.configure(image=None, text="Pas d'image")

# --- VUE 5 : FABRICATION (Split Screen & Logic) ---
class ManufacturingView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="< Retour", width=100, fg_color="transparent", border_width=1,
                      command=lambda: controller.show_frame("MenuView")).pack(side="left", padx=10, pady=10)
        
        # Split Screen : Liste à gauche, Edit à droite
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)

        # --- GAUCHE : LISTE ET FILTRES ---
        self.left_panel = ctk.CTkFrame(self.body, width=350)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Filtres
        self.filter_frame = ctk.CTkFrame(self.left_panel)
        self.filter_frame.pack(fill="x", padx=5, pady=5)
        
        self.filters = {}
        # On ajoute Cancel pour voir qu'on ne peut pas le modifier
        states = [("confirmed", "Conf."), ("progress", "En cours"), ("done", "Fait"), ("cancel", "Annul.")]
        for key, label in states:
            # Par défaut tout coché sauf cancel
            var = ctk.StringVar(value="on" if key != "cancel" else "off")
            cb = ctk.CTkCheckBox(self.filter_frame, text=label, variable=var, onvalue="on", offvalue="off",
                                 width=60, font=("Arial", 10),
                                 command=lambda: threading.Thread(target=self.on_show).start())
            cb.pack(side="left", padx=2, pady=5)
            self.filters[key] = var

        # Liste Scrollable
        self.scroll_of = ctk.CTkScrollableFrame(self.left_panel, label_text="Sélectionner un OF")
        self.scroll_of.pack(fill="both", expand=True, padx=5, pady=5)

        # --- DROITE : EDITION ---
        self.edit_panel = ctk.CTkFrame(self.body)
        self.edit_panel.pack(side="right", fill="both", expand=True)

        # Contenu par défaut (vide)
        self.lbl_placeholder = ctk.CTkLabel(self.edit_panel, text="Sélectionnez un OF pour voir les détails", text_color="grey")
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # Contenu d'édition (caché au début)
        self.edit_content = ctk.CTkFrame(self.edit_panel, fg_color="transparent")
        
        self.lbl_of_name = ctk.CTkLabel(self.edit_content, text="", font=("Roboto Medium", 22))
        self.lbl_of_name.pack(pady=20)

        self.lbl_of_status = ctk.CTkLabel(self.edit_content, text="", font=("Roboto", 16))
        self.lbl_of_status.pack(pady=10)

        self.input_frame = ctk.CTkFrame(self.edit_content)
        self.input_frame.pack(pady=20)
        
        ctk.CTkLabel(self.input_frame, text="Quantité Produite :").pack(side="left", padx=10)
        self.entry_qty = ctk.CTkEntry(self.input_frame, width=80)
        self.entry_qty.pack(side="left", padx=10)
        self.lbl_target = ctk.CTkLabel(self.input_frame, text="/ ???")
        self.lbl_target.pack(side="left", padx=10)

        self.btn_save = ctk.CTkButton(self.edit_content, text="Enregistrer Production", 
                                      fg_color="#2CC985", hover_color="#25A970",
                                      command=self.save_production)
        self.btn_save.pack(pady=20)

        self.current_order = None

    def on_show(self):
        active_filters = [k for k, v in self.filters.items() if v.get() == "on"]
        orders = self.controller.api.get_manufacturing_orders(states_filter=active_filters)
        self.after(0, lambda: self.update_list(orders))

    def update_list(self, orders):
        for widget in self.scroll_of.winfo_children():
            widget.destroy()

        if not orders:
            ctk.CTkLabel(self.scroll_of, text="Aucun OF trouvé").pack(pady=20)
            return

        for order in orders:
            # Carte cliquable
            card = ctk.CTkButton(self.scroll_of, 
                                 text=f"{order['name']}\n{order['product_id'][1]}", 
                                 height=60, fg_color="transparent", border_width=1, border_color="grey",
                                 anchor="w",
                                 command=lambda o=order: self.load_detail(o))
            card.pack(fill="x", pady=2)
            
            # Petit badge d'état à droite du bouton (visuel)
            color = "#E53935" if order['state'] == 'cancel' else "#43A047" if order['state'] == 'done' else "#FB8C00"
            state_ind = ctk.CTkLabel(card, text="●", text_color=color, font=("Arial", 20))
            state_ind.place(relx=0.9, rely=0.5, anchor="center")

    def load_detail(self, order):
        self.current_order = order
        self.lbl_placeholder.place_forget()
        self.edit_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mise à jour infos
        self.lbl_of_name.configure(text=f"{order['name']}\n{order['product_id'][1]}")
        self.lbl_of_status.configure(text=f"État : {order['state'].upper()}")
        
        # Logique d'affichage selon l'état
        # SEULEMENT 'confirmed' et 'progress' sont éditables
        if order['state'] in ['confirmed', 'progress']:
            self.input_frame.pack(pady=20)
            self.btn_save.pack(pady=20)
            self.lbl_of_status.configure(text_color="#FB8C00") # Orange
            
            # Remplissage
            self.entry_qty.delete(0, 'end')
            done_qty = order.get('qty_producing', 0)
            self.entry_qty.insert(0, str(done_qty))
            self.lbl_target.configure(text=f"/ {order['product_qty']}")
        else:
            # Mode Lecture Seule
            self.input_frame.pack_forget()
            self.btn_save.pack_forget()
            
            color = "#43A047" if order['state'] == 'done' else "#E53935"
            self.lbl_of_status.configure(text=f"Ce bon est {order['state'].upper()} (Non modifiable)", text_color=color)

    def save_production(self):
        if not self.current_order: return
        try:
            new_qty = float(self.entry_qty.get())
            target = self.current_order['product_qty']
            
            # Appel API via thread pour ne pas bloquer
            def run_update():
                res = self.controller.api.update_production_qty(self.current_order['id'], new_qty, target)
                self.after(0, lambda: self.post_save(res))
            
            threading.Thread(target=run_update, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Erreur", "Valeur numérique requise")

    def post_save(self, result):
        if result == "DONE":
            messagebox.showinfo("Bravo", "OF Terminé !")
        else:
            messagebox.showinfo("Succès", "Quantité mise à jour")
        
        # Recharger la liste pour voir le changement d'état
        self.edit_content.pack_forget()
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.on_show()

if __name__ == "__main__":
    app = ModernOdooApp()
    app.mainloop()