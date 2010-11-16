import os
import glob
import re

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    _DRAW_GRAPHS = True
except:
    _DRAW_GRAPHS = False

from ..externals.configobj import ConfigObj
from ..externals import simplejson as json

from . import schema
from . import sqlutil
from .uriutil import uri_last, uri_nextlast
from .jsonutil import get_column, JsonTable, csv_to_json
from .search import Search


class Inspector(object):
    """ Database introspection interface.
    """

    def __init__(self, interface):
        """ 
            Parameters
            ----------
            interface: Interface Object
        """
        self._intf = interface

        self.datatypes = DatatypesInspector(interface)
        self.values = NamesInspector(interface)
        self.schemas = SchemasInspector(interface)

        if _DRAW_GRAPHS:
            self.draw = GraphDrawer(interface)

        self._nomenclature = {}

    def rest(self):
        def build(coll, lvl):
            for key in schema.resources_tree[coll]:
                print ' '*lvl + '+', key.upper()

                datatypes = \
                    set([self._intf.inspect._nomenclature[uri]                
                         for uri in self._intf.inspect._nomenclature.keys()
                         if uri.split('/')[-2] == key
                         ])

                if datatypes != set():
                    print ' '*lvl + '  ' + '-'*len(key)

                for datatype in datatypes:
                    print ' '*lvl + '-', datatype

                if schema.resources_tree.has_key(key):
                    build(key, lvl+4)

        print '- %s'%'PROJECTS'
        build('projects', 4)


class DatatypesInspector(object):
    """ Database introspection interface.
    """

    def __init__(self, interface):
        """ 
            Parameters
            ----------
            interface: Interface Object
        """
        self._intf = interface

    def __call__(self, pattern='*', fields_pattern=None):
        jdata = self._intf._get_json('/REST/search/elements?format=json')
        if not fields_pattern and ('*' in pattern or '?' in pattern):       
            return get_column(jdata , 'ELEMENT_NAME', pattern)
        else:
            fields = []
            for datatype in get_column(jdata , 'ELEMENT_NAME', pattern):
                fields.extend(self._datafields(datatype, fields_pattern or '*', True))

            return fields

    def _datafields(self, datatype, pattern='*', prepend_type=True):
        jdata = self._intf._get_json(
                      '/REST/search/elements/%s?format=json'%datatype)
        fields = get_column(jdata, 'FIELD_ID', pattern)

        return ['%s/%s'%(datatype, field) if prepend_type else field
                for field in fields 
                if '=' not in field and 'SHARINGSHAREPROJECT' not in field]


    def all(self, pattern='*'):
        return self.__call__(pattern)

    def fields(self, datatype, field_pattern='*'):
        return self.__call__(datatype, field_pattern)
        
    def experiments(self, project=None):
        exps = '/REST/experiments?columns=ID,xsiType'

        if project is not None:
            exps += '&project=%s'%project

#        try:
#            return list(set(get_column(self._intf._get_json(exps), 'xsiType')))
#        except:
        types = []

        for exp_type in self._intf.inspect.datatypes():
            print exp_type,

            try:
                out = self._intf._get_json('/REST/experiments?columns=ID,xsiType&xsiType=%s'%exp_type)
            except:
                print 'whut?'
                continue
            print 'alright'
            types.append(exp_type)

#            if not out.startswith('<html>'):
#                types.append(exp_type)
#                print 'ok'
#            else:
#                print 'nope'

        return types

class NamesInspector(object):
    """ Database introspection interface.
    """

    def __init__(self, interface):
        """ 
            Parameters
            ----------
            interface: Interface Object
        """
        self._intf = interface
        self._type_groups = {}

    def __call__(self, project, datatype=None):

        if datatype is not None:
            datatypes = [datatype]
        else:
            datatypes = self._intf.inspect.datatypes.experiments()            

        for exp_type in datatypes:
            for exp_name in self.experiments(exp_type, project):    
                main_template = '/projects/%s/experiments/%s'%(project, exp_name)
                self._type_groups[main_template] = exp_type

#        for entry in set(glob.glob('*xsiType*')).difference(glob.glob('*xsiType*.headers')


        for key in self._type_groups:
            ID = key.split('/')[-1]
            seps = ID

            # find separators
            for char in re.findall('[a-zA-Z0-9]', ID):
                seps = seps.replace(char, '')
            
            # find parts
            chunks = []
            for chunk in re.split('|'.join(seps), ID):
                try:
                    float(chunk)
                    chunk = '*'
                except:
                    pass

                chunks.append(chunk)

            # write template
            template = '/'.join(key.split('/')[:-1] + ['?'.join(chunks)])

            self._intf.inspect._nomenclature[template] = self._type_groups[key]

#            self._intf.inspect._nomenclature.setdefault(
#                                type_groups[key], set()).add(template)

    def field(self, datafield):
        return list(set(
            [val
             for entry in \
             Search(datafield.split('/')[0], [datafield], self._intf
                   ).where([(datafield.split('/')[0]+'/ID', 'LIKE', '%'), 'AND']
                   ).data
             for val in entry.values()
             ]))

    def projects(self):
        return get_column(self._intf._get_json('/REST/projects'), 'ID')

    def subjects(self, project=None):
        subjs = '/REST/subjects?columns=ID'
        if project is not None:
            subjs += '&project=%s'%project

        return get_column(self._intf._get_json(subjs), 'ID')

    def experiments(self, datatype=None, project=None):
        exps = '/REST/experiments?columns=ID'
        if datatype is not None:
            exps += '&xsiType=%s'%datatype
        if project is not None:
            exps += '&project=%s'%project

        return get_column(self._intf._get_json(exps), 'ID')

    def scans(self, experiment_type=None, project=None):
        return self._sub_experiment('scan', project, experiment_type)

    def assessors(self, experiment_type=None, project=None):
        return self._sub_experiment('assessor', project, experiment_type)

    def reconstructions(self, experiment_type=None, project=None):
        return self._sub_experiment('reconstruction', project, experiment_type)

    def _sub_experiment(self, sub_exp, project, experiment_type):
        values = []

        if experiment_type is None:
            for exp_type in self._intf.inspect.datatypes.experiments():
                try:
                    column = '%s/%ss/%s/id'%(exp_type.lower(), sub_exp, sub_exp)
                    sub_exps = '/REST/experiments?columns=ID,%s'%column
                    
                    if project is not None:
                        sub_exps += '&project=%s'%project
                    print sub_exps
                    values.extend(get_column(self._intf._get_json(sub_exps), column))
                except Exception, e:
                    print e
                    continue
        else:
            column = '%s/%ss/%s/id'%(experiment_type.lower(), sub_exp, sub_exp)
            sub_exps = '/REST/experiments?columns=ID,%s'%column
            if project is not None:
                sub_exps += '&project=%s'%project
            values = get_column(self._intf._get_json(sub_exps), column)

        return list(set(values))


class GraphDrawer(object):
    def __init__(self, interface):
        self._intf = interface

    def datatypes(self, project):
        self._intf.connection.set_strategy('offline')

        experiments_types = self._intf.inspect.datatypes.experiments(project)

        labels = {project:project, 'Experiments':'Experiments'}

        g = nx.Graph()

        g.add_edge(project, 'Experiments', {'weight':1})

        for exp_type in experiments_types:
            g.add_edge('Experiments', exp_type, {'weight':8})
            labels[exp_type] = exp_type

        pos = nx.graphviz_layout(g, prog='twopi', args='')

        nx.draw_networkx_nodes(g, pos, 
                               nodelist=[project], 
                               node_color='green', alpha=0.7, 
                               node_size=2500, node_shape='s')

        nx.draw_networkx_nodes(g, pos, 
                               nodelist=['Experiments'], 
                               node_color='blue', alpha=0.7, 
                               node_size=2000, node_shape='p')

        nx.draw_networkx_nodes(g, pos, 
                               nodelist=experiments_types, 
                               node_color='red', alpha=0.7, 
                               node_size=1500, node_shape='o')

        nx.draw_networkx_edges(g, pos, width=2, alpha=0.5, edge_color='black')

        nx.draw_networkx_labels(g, pos, labels,
                                alpha=0.9, font_size=8, 
                                font_color='black', font_weight='bold')

        plt.axis('off')
        plt.show()

        self._intf.connection.revert_strategy()


class SchemasInspector(object):
    def __init__(self, interface):
        self._intf = interface

    def __call__(self):
        self._intf.manage.schemas._init()

        for xsd in self._intf.manage.schemas():
            print '-'*40
            print xsd.upper()
            print '-'*40
            print

            for datatype in schema.datatypes(self._intf.manage.schemas._trees[xsd]):
                print '[%s]'%datatype
                print

                for path in schema.datatype_attributes(
                    self._intf.manage.schemas._trees[xsd], datatype):
                        print path

                print

    def look_for(self, element_name, datatype_name=None):
        paths = []
        self._intf.manage.schemas._init()

        if ':' in element_name:
            for root in self._intf.manage.schemas._trees.values():
                paths.extend(schema.datatype_attributes(root, element_name))
            return paths


        for xsd in self._intf.manage.schemas(): 
            nsmap = self._intf.manage.schemas._trees[xsd].nsmap

            if datatype_name is not None:
                datatypes = [datatype_name]
            else:
                datatypes = schema.datatypes(self._intf.manage.schemas._trees[xsd])

            for datatype in datatypes:
                for path in schema.datatype_attributes(self._intf.manage.schemas._trees[xsd], datatype):
                    if element_name in path:
                        paths.append(path)

        return paths

