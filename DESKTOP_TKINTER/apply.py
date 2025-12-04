import tkinter as tk
from tkinter import messagebox
import xmlrpc.client
 
class OdooViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualiseur Odoo - Ma Société")
        self.root.geometry("500x500")
 
        # --- Variables de session ---
        self.uid = None
        self.models_proxy = None # Ce sera notre accès aux données
 
        # --- Config par défaut ---
        self.default_url = "http://localhost:8069"
        self.default_db = "odoo" # Mets ici ton nom de BDD corrigé
        self.default_user = "admin"
        self.default_pass = "admin"
 
        self.create_login_widgets()
        self.create_data_widgets()
 
    def create_login_widgets(self):
        # Frame de connexion
        self.frm_login = tk.LabelFrame(self.root, text="Connexion", padx=10, pady=10)
        self.frm_login.pack(padx=10, pady=10, fill="x")
 
        # Inputs simples
        tk.Label(self.frm_login, text="URL:").grid(row=0, column=0, sticky="e")
        self.entry_url = tk.Entry(self.frm_login)
        self.entry_url.insert(0, self.default_url)
        self.entry_url.grid(row=0, column=1, sticky="ew")
 
        tk.Label(self.frm_login, text="DB:").grid(row=1, column=0, sticky="e")
        self.entry_db = tk.Entry(self.frm_login)
        self.entry_db.insert(0, self.default_db)
        self.entry_db.grid(row=1, column=1, sticky="ew")
 
        tk.Label(self.frm_login, text="User:").grid(row=2, column=0, sticky="e")
        self.entry_user = tk.Entry(self.frm_login)
        self.entry_user.insert(0, self.default_user)
        self.entry_user.grid(row=2, column=1, sticky="ew")
 
        tk.Label(self.frm_login, text="Pass:").grid(row=3, column=0, sticky="e")
        self.entry_pass = tk.Entry(self.frm_login, show="*")
        self.entry_pass.insert(0, self.default_pass)
        self.entry_pass.grid(row=3, column=1, sticky="ew")
 
        tk.Button(self.frm_login, text="Connexion", command=self.connect_odoo).grid(row=4, column=0, columnspan=2, pady=10)
 
    def create_data_widgets(self):
        # Frame pour afficher les données (cachée au début)
        self.frm_data = tk.LabelFrame(self.root, text="Fiche Entreprise (res.company)", padx=10, pady=10)
        # On prépare les labels où on injectera le texte
        self.lbl_name = tk.Label(self.frm_data, text="---", font=("Arial", 14, "bold"))
        self.lbl_name.pack(pady=5)
 
        self.lbl_email = tk.Label(self.frm_data, text="Email: ---")
        self.lbl_email.pack(anchor="w")
 
        self.lbl_phone = tk.Label(self.frm_data, text="Tel: ---")
        self.lbl_phone.pack(anchor="w")
 
        self.lbl_currency = tk.Label(self.frm_data, text="Devise: ---")
        self.lbl_currency.pack(anchor="w")
 
    def connect_odoo(self):
        url = self.entry_url.get()
        self.db = self.entry_db.get() # On stocke db et pass car on en aura besoin pour chaque requête
        self.password = self.entry_pass.get()
        username = self.entry_user.get()
 
        try:
            # 1. Authentification (Endpoint COMMON)
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, username, self.password, {})
 
            if self.uid:
                messagebox.showinfo("Succès", f"Connecté ! UID: {self.uid}")
                # 2. Préparation pour les données (Endpoint OBJECT)
                self.models_proxy = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                # 3. On lance la récupération des infos
                self.fetch_company_info()
            else:
                messagebox.showerror("Erreur", "Mauvais identifiants")
 
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
 
    def fetch_company_info(self):
        # C'est ici que la magie opère
        try:
            # On cherche dans le modèle 'res.company'
            # execute_kw(db, uid, password, model, method, query)
            # search_read est une méthode puissante : elle cherche ET lit les données en une fois
            # [[], ...] -> La liste vide signifie "Tous les enregistrements" (pas de filtre)
            # {'limit': 1} -> On en prend juste un (le premier, c'est souvent la boite principale)
            fields_to_get = ['name', 'email', 'phone', 'currency_id']
            companies = self.models_proxy.execute_kw(
                self.db, self.uid, self.password,
                'res.company', 'search_read',
                [[]], 
                {'fields': fields_to_get, 'limit': 1}
            )
 
            if companies:
                data = companies[0] # On prend le premier dictionnaire de la liste
                print(f"Données reçues d'Odoo : {data}") # Regarde ta console pour voir le format brut !
 
                # Mise à jour de l'IHM
                self.frm_data.pack(padx=10, pady=10, fill="both", expand=True) # On affiche le panneau
                self.lbl_name.config(text=data.get('name', 'Inconnu'))
                self.lbl_email.config(text=f"Email: {data.get('email', 'N/A')}")
                self.lbl_phone.config(text=f"Tel: {data.get('phone', 'N/A')}")
                # currency_id est spécial : Odoo renvoie souvent [id, "Nom"] (ex: [1, "EUR"])
                currency = data.get('currency_id')
                currency_text = currency[1] if currency else "N/A"
                self.lbl_currency.config(text=f"Devise: {currency_text}")
 
        except Exception as e:
            messagebox.showerror("Erreur lecture", str(e))
 
if __name__ == "__main__":
    root = tk.Tk()
    app = OdooViewerApp(root)
    root.mainloop()