import urllib

def flash_properties_to_dict(propertysheet, portal_url):
    items = dict()
    
    if not portal_url.endswith('/'):
        portal_url += '/'
    # build python representation of properties first
    for key, value in propertysheet.propertyItems():
        if key.startswith('param/'):
            # process param/ properties only
            if isinstance(value, str):
                new_value = value.replace('${portal_path}', portal_url)
                new_value = new_value.replace('${portal_url}', portal_url)
            else:
                new_value = value
            # key name is param/src - there must be 'src' only in result dict
            items[key[6:]] = new_value
    return items
            

def properties_to_dict(propertysheet, portal_url, ignore=['title']):
    """
    Analyses portal properties and creates python dictionary from keys-values. 
    Key in the form 'k1/k2/k3' having a value 'value' is transformed to dictionary:
    items = { k1 : { k2 : { k3 : value } } }
    """
    items = dict()
    
    if not portal_url.endswith('/'):
        portal_url += '/'
    
    # build python representation of properties first
    for key, value in propertysheet.propertyItems():
        if key in ignore:
            continue
            
        # automatically ignore all properties starting with 'param/' - these are flash properties
        if key.startswith('param/'):
            continue
            
        if isinstance(value, str):
            new_value = value.replace('${portal_path}', portal_url)
            new_value = new_value.replace('${portal_url}', portal_url)
        else:
            new_value = value
            
        # quote any key with /url in it, because we can't pass ++resource++ 
        # to the flash as argument - it will replace + with space and file 
        # is not found.
        if key.endswith('/url'):
            new_value = urllib.quote(new_value)

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
                    to_fill[k] = new_value
            else:
                to_fill = to_fill[k]

    return items
