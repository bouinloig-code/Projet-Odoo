import xmlrpc.client
import threading
 
class OdooClient:
    def __init__(self, url, db):
        self.url = url
        self.db = db
        # On sépare les endpoints pour la clarté
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        self.uid = None
        self.password = None
 
    def login(self, username, password):
        try:
            uid = self.common.authenticate(self.db, username, password, {})
            if uid:
                self.uid = uid
                self.password = password
                return True
            return False
        except Exception as e:
            print(f"Erreur Login: {e}")
            return False
 
    def search_read(self, model, fields, domain=None, limit=100):
        if domain is None: domain = []
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search_read',
                [domain],
                {'fields': fields, 'limit': limit}
            )
        except Exception as e:
            print(f"Erreur API ({model}): {e}")
            return []
 
    # --- Méthodes Métier ---
 
    def get_company_info(self):
        """Récupère les infos complètes (Logo + Adresse)"""
        # On ajoute 'logo', 'street', 'zip', 'city'
        fields = ['name', 'email', 'phone', 'vat', 'street', 'zip', 'city', 'logo']
        data = self.search_read('res.company', fields, limit=1)
        return data[0] if data else {}
 
    def get_products(self, limit=100):
        # Optimisation : On ne charge pas 8000 produits d'un coup pour l'instant
        # On demande aussi 'uom_id' (Unité de mesure) c'est souvent utile
        return self.search_read('product.product', 
                              ['name', 'list_price', 'qty_available', 'image_1920', 'default_code'], 
                              limit=limit)
 
    def get_manufacturing_orders(self, states_filter=None):
        domain = []
        if states_filter:
            domain = [['state', 'in', states_filter]]
        # On ajoute qty_producing pour ne pas avoir d'erreur
        return self.search_read('mrp.production', 
                                ['name', 'product_id', 'product_qty', 'qty_producing', 'state'], 
                                domain=domain, limit=100)
    def update_production_qty(self, mo_id, new_qty, target_qty):
        try:
            self.models.execute_kw(self.db, self.uid, self.password,
                                 'mrp.production', 'write',
                                 [[mo_id], {'qty_producing': float(new_qty)}])
            if float(new_qty) >= float(target_qty):
                self.models.execute_kw(self.db, self.uid, self.password,
                                     'mrp.production', 'button_mark_done',
                                     [[mo_id]])
                return "DONE"
            return "UPDATED"
        except Exception as e:
            print(f"Erreur Update OF: {e}")
            raise e