import simplejson
import urllib

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
            new_value = value.replace('${portal_path}', portal_path)
        else:
            new_value = value
            
        # quote any key with /url in it, because we can't pass ++resource++ 
        # to the flash as argument - it will replace + with space and file 
        # is not found.
        if '/url' in key:
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

    if as_json_string:
        return simplejson.dumps(items)
    else:
        return items
