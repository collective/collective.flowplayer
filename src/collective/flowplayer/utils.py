import simplejson

def properties_to_javascript(propertysheet, portal, ignore=['title'], as_json_string=False):
    items = dict()
    
    portal_path = portal.absolute_url_path()
    if not portal_path.endswith('/'):
        portal_path += '/'
    
    # build python representation of properties first
    for key, value in propertysheet.propertyItems():
        if key in ignore:
            continue
        
        if isinstance(value, str):
            js_repr = value.replace('${portal_path}', portal_path)
        else:
            js_repr = value

        keys = key.split('/')
        to_fill = items
        for idx, k in enumerate(keys):
            if not k:
                continue
            if not to_fill.has_key(k):
                if idx < len(keys)-1:
                    to_fill[k] = dict()
                    to_fill = to_fill[k]
                else:
                    to_fill[k] = js_repr
            else:
                to_fill = to_fill[k]

    if as_json_string:
        return simplejson.dumps(items)
    else:
        return items
