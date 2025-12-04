import xmlrpc.client
 
class OdooClient:
    def __init__(self, url, db):
        self.url = url
        self.db = db
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        self.uid = None
        self.password = None
 
    def login(self, username, password):
        """Tente de se connecter et stocke l'UID en cas de succès"""
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
 
    def search_read(self, model, fields, domain=None, limit=None):
        """Méthode générique pour lire des données"""
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
 
    # --- Méthodes Métier Spécifiques ---
 
    def get_company_info(self):
        """Récupère les infos de la première société trouvée"""
        data = self.search_read('res.company', ['name', 'email', 'phone', 'vat'], limit=1)
        return data[0] if data else {}
 
    def get_products(self, limit=20):
        """Récupère une liste de produits avec image"""
        return self.search_read('product.product', 
                              ['name', 'list_price', 'qty_available', 'image_1920'], 
                              limit=limit)

    def get_manufacturing_orders(self, states_filter=None, limit=20):
        """Récupère la liste des ordres de fabrication"""
        domain = []
        if states_filter:
            domain = [['state', 'in', states_filter]]

        return self.search_read('mrp.production', 
                                ['name', 'product_id', 'product_qty', 'state'], 
                                domain=domain, limit=limit)