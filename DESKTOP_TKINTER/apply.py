import tkinter as tk
from tkinter import messagebox
import xmlrpc.client
 
class OdooConnectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Connexion Odoo")
        self.root.geometry("400x350")
 
        # --- Configuration par défaut (A adapter à ton Docker) ---
        # Si ton docker est mappé sur le port 8069 de ta VM :
        self.default_url = "http://localhost:8069" 
        self.default_db = "demo"
        self.default_user = "bouin.loig@gmail.com"
        self.default_pass = "MSIR5"
 
        self.create_widgets()
 
    def create_widgets(self):
        # URL
        tk.Label(self.root, text="URL Odoo (ex: http://localhost:8069)").pack(pady=5)
        self.entry_url = tk.Entry(self.root, width=40)
        self.entry_url.insert(0, self.default_url)
        self.entry_url.pack()
 
        # Database
        tk.Label(self.root, text="Base de données (Nom)").pack(pady=5)
        self.entry_db = tk.Entry(self.root, width=40)
        self.entry_db.insert(0, self.default_db)
        self.entry_db.pack()
 
        # User
        tk.Label(self.root, text="Email / Utilisateur").pack(pady=5)
        self.entry_user = tk.Entry(self.root, width=40)
        self.entry_user.insert(0, self.default_user)
        self.entry_user.pack()
 
        # Password
        tk.Label(self.root, text="Mot de passe / API Key").pack(pady=5)
        self.entry_pass = tk.Entry(self.root, show="*", width=40)
        self.entry_pass.insert(0, self.default_pass)
        self.entry_pass.pack()
 
        # Status Label
        self.lbl_status = tk.Label(self.root, text="En attente...", fg="grey")
        self.lbl_status.pack(pady=20)
 
        # Button
        btn_connect = tk.Button(self.root, text="Tester la connexion", command=self.test_connection)
        btn_connect.pack(pady=5)
 
    def test_connection(self):
        url = self.entry_url.get().strip()
        db = self.entry_db.get().strip()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
 
        # Le endpoint 'common' sert uniquement à l'authentification et aux infos de version
        # C'est la porte d'entrée.
        common_endpoint = f'{url}/xmlrpc/2/common'
 
        try:
            self.lbl_status.config(text="Tentative de connexion...", fg="blue")
            self.root.update() # Force le rafraichissement UI
 
            # Création du proxy XML-RPC
            common = xmlrpc.client.ServerProxy(common_endpoint)
 
            # Demande d'authentification
            # La méthode 'authenticate' renvoie l'UID (int) si succès, ou False/Error
            uid = common.authenticate(db, username, password, {})
 
            if uid:
                msg = f"SUCCÈS ! Connecté avec l'UID : {uid}"
                self.lbl_status.config(text=msg, fg="green")
                print(f"[DEBUG] Authentification réussie. UID: {uid}")
            else:
                self.lbl_status.config(text="Échec : Mauvais identifiants ?", fg="red")
 
        except ConnectionRefusedError:
            self.lbl_status.config(text="Erreur : Connexion refusée (Vérifie Docker/Port)", fg="red")
        except Exception as e:
            self.lbl_status.config(text=f"Erreur technique : {str(e)}", fg="red")
            print(f"[DEBUG] Erreur : {e}")
 
if __name__ == "__main__":
    root = tk.Tk()
    app = OdooConnectorApp(root)
    root.mainloop()