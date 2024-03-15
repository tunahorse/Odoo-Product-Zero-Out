


import ssl
import xmlrpc.client

# Configuration for the Odoo server connection
config = {
    'db': 'local',
    'url': 'http://localhost:8069',
    'username': 'local',
    'password': 'local',
}

# Initialize SSL context for unverified HTTPS connections
def init_ssl_context():
    try:
        return ssl._create_unverified_context()
    except AttributeError:
        # This part of the code will only execute for very old versions of Python that do not support ssl._create_unverified_context
        return None

# Create XML-RPC server proxies for 'object' and 'common' interfaces
def create_server_proxy(path, ssl_context):
    server_proxy_url = '{}/xmlrpc/2/{}'.format(config['url'], path)
    return xmlrpc.client.ServerProxy(server_proxy_url, allow_none=True, verbose=False, use_datetime=True, context=ssl_context)

# Authenticate the user and return the uid
def authenticate(ssl_context):
    common = create_server_proxy('common', ssl_context)
    return common.authenticate(config['db'], config['username'], config['password'], {})

# Fetch product information by barcode
def get_product_info(models, uid, barcode):
    product = models.execute_kw(config['db'], uid, config['password'],
                                'product.product', 'search_read',
                                [[['barcode', '=', barcode]]],
                                {'fields': ['name', 'id']})
    return product

# Reset stock quantities to zero for a given product
def reset_stock_quantities(models, uid, product_id):
    on_hand_data = models.execute_kw(config['db'], uid, config['password'],
                                     'stock.quant', 'search_read', 
                                     [[['product_id', '=', product_id]]])
    
    for quant in on_hand_data:
        models.execute_kw(config['db'], uid, config['password'], 'stock.quant', 'write',
                          [quant['id'], {'quantity': 0, 'reserved_quantity': 0}])
        print(f"Reset to zero for location {quant['location_id']} and lot {quant['lot_id']}")

if __name__ == '__main__':
    ssl_context = init_ssl_context()
    models = create_server_proxy('object', ssl_context)
    uid = authenticate(ssl_context)
    barcode = '123'  # Example barcode, you can user any product.product or product.template identifier here instead like name,id,lot_code ect.
    product = get_product_info(models, uid, barcode)
    if product:
        reset_stock_quantities(models, uid, product[0]['id'])
    else:
        print("Product not found.")
