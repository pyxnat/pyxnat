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

#class Inspector(object):
#    """ Database introspection interface.
#    """

#    def __init__(self, interface):
#        """ 
#            Parameters
#            ----------
#            interface: Interface Object
#        """
#        self._intf = interface
#        self._nomenclature = {}

#    def __call__(self, project, subjects_nb=2, universal=False):
#        """ Inspects an existing and already populated project of a XNAT server.
#            The idea is to gather some information about the kind of data that
#            is indexed in the project to help the users find their way in browsing
#            and uploading data.

#            Parameters
#            ----------
#            project: string
#                An existing project name.
#            subjects_nb: int
#                A number of subjects has to be explored in order to discover
#                the types of data on the server. Too much subjects and it may
#                take forever. To few and you may capture only part of the data
#                on the server. The default is 2.
#            universal: True | False
#                False, the extracted information is used only for that project.
#                True, the extracted information is generalized for every projects.

#            Returns
#            -------
#            None. 
#            But updates a dictionnary which is used throughout the API to help 
#            the users. The methods that use the dictionnary are:
#                - EObject.create()
#                - interface.inspect.rest_hierarchy()
#                - interface.inspect.naming_conventions()

#        """

#        subjects = []
#        for i, s in enumerate(self._intf.select('/project/%s/subjects'%project).get('label')):
#            subjects.append(s)            

#            if i >= subjects_nb-1:
#                break

#        uri_glob = {}

#        for subject in subjects:

#            for eobj in self._intf.select('/project/%s/subject/%s'
#                                          '/experiments'%(project, subject)
#                                          ).get('obj'):

#                uri_glob.setdefault('experiments', {}
#                      ).setdefault(eobj.datatype(), []).append(eobj._uri)

#            for eobj in self._intf.select('/project/%s/subject/%s'
#                                          '/experiments/assessors'%(project, subject)
#                                          ).get('obj'):

#                uri_glob.setdefault('assessors', {}
#                      ).setdefault(eobj.datatype(), []).append(eobj._uri)

#            for eobj in self._intf.select('/project/%s/subject/%s'
#                                          '/experiments/reconstructions'%(project, subject)
#                                          ).get('obj'):

#                uri_glob.setdefault('reconstructions', {}
#                      ).setdefault(eobj.datatype(), []).append(eobj._uri)

#            for eobj in self._intf.select('/project/%s/subject/%s'
#                                          '/experiments/scans'%(project, subject)
#                                          ).get('obj'):

#                uri_glob.setdefault('scans', {}
#                      ).setdefault(eobj.datatype(), []).append(eobj._uri)


#        xsi_map = {}

#        level_keywords = {'projects':set([project]),
#                          'subjects':set(subjects)}

#        if universal:
#            project = '*'

#        if uri_glob.has_key('experiments'):
#            for datatype in uri_glob['experiments'].keys():
#                for uri in uri_glob['experiments'][datatype]:
#                    kw = self._intf.select(uri).label() or self._intf.select(uri).id()

#                    for ancestor in ['projects', 'subjects']:
#                        for ancestor_kw in level_keywords[ancestor]:
#                            kw = kw.replace(ancestor_kw, '*')

#                    level_keywords.setdefault('experiments', set()).add(kw)
#                    xsi_map.setdefault('/projects/%s/subjects/*/experiments/%s'%(project, kw), datatype)

#        if uri_glob.has_key('assessors'):
#            for datatype in uri_glob['assessors'].keys():
#                for uri in uri_glob['assessors'][datatype]:
#                    kw = self._intf.select(uri).label() or self._intf.select(uri).id()

#                    for ancestor in ['projects', 'subjects', 'experiments']:
#                        for ancestor_kw in level_keywords[ancestor]:
#                            kw = kw.replace(ancestor_kw, '*')

#                    level_keywords.setdefault('assessors', set()).add(kw)
#                    xsi_map.setdefault('/projects/%s/subjects/*'
#                                       '/experiments/*/assessors/%s'%(project, kw), datatype)

#        if uri_glob.has_key('reconstructions'):
#            for datatype in uri_glob['reconstructions'].keys():
#                for uri in uri_glob['reconstructions'][datatype]:
#                    kw = self._intf.select(uri).label() or self._intf.select(uri).id()

#                    for ancestor in ['projects', 'subjects', 'experiments']:
#                        for ancestor_kw in level_keywords[ancestor]:
#                            kw = kw.replace(ancestor_kw, '*')

#                    level_keywords.setdefault('reconstructions', set()).add(kw)
#                    xsi_map.setdefault('/projects/%s/subjects/*'
#                                       '/experiments/*/reconstructions/%s'%(project, kw), datatype)

#        if uri_glob.has_key('scans'):
#            for datatype in uri_glob['scans'].keys():
#                for uri in uri_glob['scans'][datatype]:
#                    kw = self._intf.select(uri).label() or self._intf.select(uri).id()

#                    for ancestor in ['projects', 'subjects', 'experiments']:
#                        for ancestor_kw in level_keywords[ancestor]:
#                            kw = kw.replace(ancestor_kw, '*')

#                    level_keywords.setdefault('scans', set()).add(kw)
#                    xsi_map.setdefault('/projects/%s/subjects/*'
#                                       '/experiments/*/scans/%s'%(project, kw), datatype)

#        self._nomenclature.update(xsi_map)

#    def experiments(self, datatype=None):
#        if datatype is None:
#            exps = '/REST/experiments?columns=ID'
#        else:
#            exps = '/REST/experiments?columns=ID&xsiType=%s'%datatype

#        return get_column(self._intf._get_json(exps), 'ID')

#    def _sub_experiment(self, sub_exp):
##        exps = '/REST/experiments?columns=ID,xsiType'
##        exps_types = set(get_column(self._intf._get_json(exps), 'xsiType'))

#        header = 'xnat:imagesessiondata/%ss/%s/id'%(sub_exp, sub_exp)

#        sub_exps = '/REST/experiments?columns=ID,%s'%header
#        jtable = JsonTable(self._intf._get_json(sub_exps), ['ID', header])
# 
#        for ID, sub_id in jtable.select(['ID', header]).items():
#            yield ID, sub_id

#    def scans(self):
#        return [(a, b) for a, b in self._sub_experiment('scan')]

#    def assessors(self):
#        return [(a, b) for a, b in self._sub_experiment('assessor')]

#    def reconstructions(self):
#        return [(a, b) for a, b in self._sub_experiment('reconstruction')]

#    def save(self, location):
#        if os.path.exists(location):
#            os.remove(location)

#        cfg = ConfigObj(location)
#        cfg.update(self._nomenclature)
#        cfg.write()

#    def update(self, location):
#        self._nomenclature.update(ConfigObj(location).dict())

#    def clear(self):
#        self._nomenclature = {}

#    def naming_conventions(self, as_graph=False):
#        if not as_graph:
#            return self._nomenclature

#        import networkx as nx
#        import matplotlib.pyplot as plt

#        gnom = nx.Graph()

#        proj_nodes = set()
#        rest_nodes = set()
#        xsi_nodes  = set()
#        name_nodes = set()

#        labels = {}
#        conv_labels = {}

#        for uri_pattern in self._nomenclature.keys():

#            proj_name = uri_pattern.split('/')[2]
#            rest_name = '%s_%s'%(uri_pattern.split('/')[2], uri_nextlast(uri_pattern))
#            xsi_name = '%s_%s'%(uri_pattern.split('/')[2], self._nomenclature[uri_pattern])
#            conv_name = '%s_%s'%(uri_pattern.split('/')[2], uri_last(uri_pattern))

#            proj_nodes.add(proj_name)
#            rest_nodes.add(rest_name)
#            xsi_nodes.add(xsi_name)
#            name_nodes.add(conv_name)

#            labels[proj_name] = proj_name
#            labels[rest_name] = uri_nextlast(uri_pattern)
#            labels[xsi_name] = self._nomenclature[uri_pattern]
#            conv_labels[conv_name] = uri_last(uri_pattern)

#            gnom.add_edge(proj_name, rest_name, {'weight':1})
#            gnom.add_edge(rest_name, xsi_name, {'weight':8})
#            gnom.add_edge(xsi_name, conv_name, {'weight':2})

#        pos = nx.graphviz_layout(gnom, prog='twopi', args='')

#        nx.draw_networkx_nodes(gnom, pos, 
#                               nodelist=list(proj_nodes), 
#                               node_color='red', alpha=0.7, 
#                               node_size=1500, node_shape='o')
#        
#        nx.draw_networkx_nodes(gnom, pos, 
#                               nodelist=list(rest_nodes), 
#                               node_color='blue', alpha=0.7, 
#                               node_size=1000, node_shape='o')

#        nx.draw_networkx_nodes(gnom, pos, 
#                               nodelist=list(xsi_nodes), 
#                               node_color='blue', alpha=0.5, 
#                               node_size=500, node_shape='o')

#        nx.draw_networkx_nodes(gnom, pos, 
#                               nodelist=list(name_nodes), 
#                               node_color='blue', alpha=0.3, 
#                               node_size=250, node_shape='o')

#        nx.draw_networkx_edges(gnom, pos, width=2, alpha=0.5, edge_color='black')

#        nx.draw_networkx_labels(gnom, pos, labels,
#                                alpha=0.9, font_size=8, 
#                                font_color='black', font_weight='bold')

#        nx.draw_networkx_labels(gnom, pos, conv_labels,
#                                alpha=0.9, font_size=6, 
#                                font_color='black')

#        plt.axis('off')
#        plt.show()

#    def rest_hierarchy(self, as_graph=False):
#        if as_graph:
#            import networkx as nx
#            import matplotlib.pyplot as plt
#            gnom = nx.Graph()

#            proj_nodes = set()
#            rest_nodes = set()
#            xsi_nodes  = set()

#            labels = {}

#            for uri_pattern in self._nomenclature.keys():
#                proj_name = uri_pattern.split('/')[2]
#                rest_name = '%s_%s'%(uri_pattern.split('/')[2], uri_nextlast(uri_pattern))
#                xsi_name = '%s_%s'%(uri_pattern.split('/')[2], self._nomenclature[uri_pattern])

#                proj_nodes.add(proj_name)
#                rest_nodes.add(rest_name)
#                xsi_nodes.add(xsi_name)

#                labels[proj_name] = proj_name
#                labels[rest_name] = uri_nextlast(uri_pattern)
#                labels[xsi_name] = self._nomenclature[uri_pattern]

#                gnom.add_edge(proj_name, rest_name, {'weight':1})
#                gnom.add_edge(rest_name, xsi_name, {'weight':8})

#            pos = nx.graphviz_layout(gnom, prog='twopi', args='')

#            nx.draw_networkx_nodes(gnom, pos, 
#                                   nodelist=list(proj_nodes), 
#                                   node_color='red', alpha=0.7, 
#                                   node_size=1500, node_shape='o')
#            
#            nx.draw_networkx_nodes(gnom, pos, 
#                                   nodelist=list(rest_nodes), 
#                                   node_color='blue', alpha=0.7, 
#                                   node_size=1000, node_shape='o')

#            nx.draw_networkx_nodes(gnom, pos, 
#                                   nodelist=list(xsi_nodes), 
#                                   node_color='blue', alpha=0.5, 
#                                   node_size=500, node_shape='o')

#            nx.draw_networkx_edges(gnom, pos, width=2, alpha=0.5, edge_color='black')

#            nx.draw_networkx_labels(gnom, pos, labels,
#                                    alpha=0.9, font_size=8, 
#                                    font_color='black', font_weight='bold')

#            plt.axis('off')
#            plt.show()
#            return

#        def build(coll, lvl):
#            for key in schema.resources_tree[coll]:
#                print ' '*lvl + '+', key.upper()

#                datatypes = \
#                    set([self._intf.inspect._nomenclature[uri]                
#                         for uri in self._intf.inspect._nomenclature.keys()
#                         if uri.split('/')[-2] == key
#                         ])

#                if datatypes != set():
#                    print ' '*lvl + '  ' + '-'*len(key)

#                for datatype in datatypes:
#                    print ' '*lvl + '-', datatype

#                if schema.resources_tree.has_key(key):
#                    build(key, lvl+4)

#        print '- %s'%'PROJECTS'
#        build('projects', 4)

#    def datatypes(self, pattern='*', fields_pattern=None):
#        jdata = self._intf._get_json('/REST/search/elements?format=json')
#        if not fields_pattern and ('*' in pattern or '?' in pattern):       
#            return get_column(jdata , 'ELEMENT_NAME', pattern)
#        else:
#            fields = []
#            for datatype in get_column(jdata , 'ELEMENT_NAME', pattern):
#                fields.extend(self._datafields(datatype, fields_pattern or '*', True))

#            return fields

#    def _datafields(self, datatype, pattern='*', prepend_type=True):
#        jdata = self._intf._get_json(
#                      '/REST/search/elements/%s?format=json'%datatype)
#        fields = get_column(jdata, 'FIELD_ID', pattern)

#        return ['%s/%s'%(datatype, field) if prepend_type else field
#                for field in fields 
#                if '=' not in field and 'SHARINGSHAREPROJECT' not in field]

#    def fieldvalues(self, datafield):
#        return list(set(
#            [val
#             for entry in \
#             Search(datafield.split('/')[0], [datafield], self._intf
#                   ).where([('xnat:subjectData/SUBJECT_ID', 'LIKE', '%'), 'AND']
#                   ).data
#             for val in entry.values()
#             ]))



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

        if _DRAW_GRAPHS:
            self.draw = GraphDrawer(interface)

        self._nomenclature = {}

    def schemas(self):
        for xsd in self._intf.manage.schemas.names():
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

        return list(set(get_column(self._intf._get_json(exps), 'xsiType')))


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

    def __call__(self, project, datatype=None):
        type_groups = {}

        if datatype is not None:
            datatypes = [datatype]
        else:
            datatypes = self._intf.inspect.datatypes.experiments()            

        for exp_type in datatypes:
            for exp_name in self.experiments(exp_type, project):    
                main_template = '/projects/%s/experiments/%s'%(project, exp_name)
                type_groups[main_template] = exp_type

        for key in type_groups:
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
            template = '/'+'/'.join(key.split('/')[-2:-1] + ['?'.join(chunks)])

            self._intf.inspect._nomenclature[template] = type_groups[key]

#            self._intf.inspect._nomenclature.setdefault(
#                                type_groups[key], set()).add(template)

    def field(self, datafield):
        return list(set(
            [val
             for entry in \
             Search(datafield.split('/')[0], [datafield], self._intf
                   ).where([('xnat:subjectData/SUBJECT_ID', 'LIKE', '%'), 'AND']
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


