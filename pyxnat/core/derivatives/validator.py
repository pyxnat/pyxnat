XNAT_RESOURCE_NAMES = ['BBRC_VALIDATOR']

def tests(self, name, key=None):
    import json
    j = [e for e in list(self.files(name)) if 'json' in e._urn][0]
    j = json.loads(self._intf.get(j._uri).text)
    if key is None:
        return j
    else:
        return j[key]
