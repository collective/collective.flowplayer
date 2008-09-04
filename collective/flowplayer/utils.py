
def properties_to_javascript(propertysheet, ignore=['title']):
    
    items = {}
    
    for key, value in propertysheet.propertyItems():
        if key in ignore:
            continue
        
        js_repr = repr(value)
        if isinstance(value, bool):
            js_repr = js_repr.lower()
        items[key] = js_repr
    
    return "{ %s }" % ',\n'.join(["%s:%s" % (k, v) for k,v in items.items()])