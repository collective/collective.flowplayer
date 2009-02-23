
def properties_to_javascript(propertysheet, portal, ignore=['title']):
    
    items = {}
    
    portal_path = portal.absolute_url_path()
    if not portal_path.endswith('/'):
        portal_path += '/'
    
    for key, value in propertysheet.propertyItems():
        if key in ignore:
            continue
        
        js_repr = repr(value)
        if isinstance(value, bool):
            js_repr = js_repr.lower()
        elif isinstance(value, str):
            js_repr = js_repr.replace('${portal_path}', portal_path)
        
        items[key] = js_repr
    
    return "{ %s }" % ',\n'.join(["%s:%s" % (k, v) for k,v in items.items()])