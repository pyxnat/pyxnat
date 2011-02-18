import glob

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    _DRAW_GRAPHS = True
except:
    _DRAW_GRAPHS = False

from ..externals import simplejson as json

from . import schema
from .jsonutil import get_column
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
        self._nomenclature = {}

        self._intf = interface
        self._get_json = interface._get_json

        self.schemas = SchemasInspector(interface)

    def datatypes(self, pattern='*', fields_pattern=None):

        search_els = self._get_json('/REST/search/elements?format=json')

        if not fields_pattern and ('*' in pattern or '?' in pattern):       
            return get_column(search_els , 'ELEMENT_NAME', pattern)

        else:
            fields = []
            for datatype in get_column(search_els , 'ELEMENT_NAME', pattern):
                fields.extend(self._datafields(datatype, 
                                               fields_pattern or '*', True)
                              )

            return fields

    def _datafields(self, datatype, pattern='*', prepend_type=True):

        search_fds = self._get_json('/REST/search/elements/%s?format=json' \
                                        % datatype
                                    )

        fields = get_column(search_fds, 'FIELD_ID', pattern)

        return ['%s/%s' % (datatype, field) 
                if prepend_type else field
                for field in fields 
                if '=' not in field and 'SHARINGSHAREPROJECT' not in field
                ]

    def experiment_types(self, project=None):
        types = []

        uri_template = self._intf._server
        uri_template += '/REST/experiments?columns=ID,xsiType&xsiType=%s'

        if project is not None:
            uri_template += '&project=%s' % project

        for exp_type in self.datatypes():
            print exp_type
            head = self._intf._conn.request(uri_template % exp_type, 
                                                'HEAD')[0]
            if head.get('status') == '200':
                types.append(exp_type)

        return types

    def field_values(self, field_name):

        search_tbl = Search(field_name.split('/')[0], 
                            [field_name], self._intf
                            )

        criteria = [('%s/ID' % field_name.split('/')[0], 'LIKE', '%'), 'AND']

        return list(set([val
                         for entry in search_tbl.where(criteria)
                         for val in entry.values()
                         ])
                    )

    def project_values(self):
        return get_column(self._get_json('/REST/projects'), 'ID')

    def subject_values(self, project=None):
        uri = '/REST/subjects?columns=ID'

        if project is not None:
            uri += '&project=%s' % project

        return get_column(self._get_json(uri), 'ID')

    def experiment_values(self, datatype=None, project=None):
        uri = '/REST/experiments?columns=ID'
        if datatype is not None:
            uri += '&xsiType=%s' % datatype
        if project is not None:
            uri += '&project=%s' % project

        return get_column(self._get_json(uri), 'ID')

    def assessor_values(self, experiment_type=None, project=None):
        return self._sub_experiment('assessor', project, experiment_type)

    def scan_values(self, experiment_type=None, project=None):
        return self._sub_experiment('scan', project, experiment_type)

    def reconstruction_values(self, experiment_type=None, project=None):
        return self._sub_experiment('reconstruction', 
                                    project, experiment_type)

    def architecture(self):
        def traverse(coll, lvl):
            for key in schema.resources_tree[coll]:
                print '%s+%s' % (' ' * lvl, key.upper())

                datatypes = set([
                        self._intf.inspect._nomenclature[uri]
                        for uri in self._intf.inspect._nomenclature.keys()
                        if uri.split('/')[-2] == key
                        ])

                if datatypes != set():
                    print '%s  %s' % (' ' * lvl, '-' * len(key))

                for datatype in datatypes:
                    print '%s- %s' % (' ' * lvl, datatype)

                if schema.resources_tree.has_key(key):
                    traverse(key, lvl + 4)

        print '- %s' % 'PROJECTS'
        traverse('projects', 4)

    def _sub_experiment(self, sub_exp, project, experiment_type):
        values = []

        if experiment_type is None:
            for exp_type in self.experiment_types():
                try:
                    column = '%s/%ss/%s/id' % \
                        (exp_type.lower(), sub_exp, sub_exp)

                    sub_exps = '/REST/experiments?columns=ID,%s' % column
                    
                    if project is not None:
                        sub_exps += '&project=%s' % project

                    values.extend(get_column(
                            self._get_json(sub_exps), column))

                except Exception, e:
                    print e
                    continue

        else:
            column = '%s/%ss/%s/id' % \
                (experiment_type.lower(), sub_exp, sub_exp)

            sub_exps = '/REST/experiments?columns=ID,%s' % column

            if project is not None:
                sub_exps += '&project=%s' % project

            values = get_column(self._get_json(sub_exps), column)

        return list(set(values))


class GraphData(object):
    def __init__(self, interface):
        self._intf = interface
        self._nomenclature = interface.inspect._nomenclature

    def link(self, subjects, fields):
        
        criteria = [('xnat:subjectData/SUBJECT_ID', '=', _id) 
                    for _id in subjects
                    ]
        criteria += ['OR']
        # variables = ['xnat:subjectData/SUBJECT_ID'] + fields

        subject_id = 'xnat:subjectData/SUBJECT_ID'

        for field in fields:

            field_tbl = self._intf.select('xnat:subjectData', 
                                          [subject_id, field]
                                          ).where(criteria)
            head = field_tbl.headers()
            head.remove('subject_id')
            head = head[0]
            possible = set(field_tbl.get(head))

            groups = {}
            
            for val in possible:
                groups[val] = field_tbl.where(**{head:val}
                                                ).select('subject_id')

        return groups

    def datatypes(self):
        graph = nx.DiGraph()
        graph.add_node('datatypes')
        graph.labels = {'datatypes':'datatypes'}
        graph.weights = {'datatypes':100.0}
        
        datatypes = self._intf.inspect.datatypes()
        namespaces = set([dat.split(':')[0] for dat in datatypes])
        
        for ns in namespaces:
            graph.add_edge('datatypes', ns)
            graph.weights[ns] = 70.0

            for dat in datatypes:
                if dat.startswith(ns):
                    graph.add_edge(ns, dat)
                    graph.weights[dat] = 40.0

        return graph

    def rest_resource(self, name):
        kbase = {}

        for kfile in glob.iglob('%s/*.struct' % self._intf._cachedir):
            kdata = json.load(open(kfile, 'rb'))
            if name in kdata.keys()[0]:
                kbase.update(kdata)

        experiment_types = set(kbase.values())

        graph = nx.DiGraph()
        graph.add_node(name)
        graph.labels = {name:name}
        graph.weights = {name:100.0}
        
        namespaces = set([exp.split(':')[0] for exp in experiment_types])
        
        for ns in namespaces:
            graph.add_edge(name, ns)
            graph.weights[ns] = 70.0

            for exp in experiment_types:
                if exp.startswith(ns):
                    graph.add_edge(ns, exp)
                    graph.weights[exp] = 40.0

        return graph

    def field_values(self, field_name):
        
        search_tbl = Search(field_name.split('/')[0], 
                            [field_name], self._intf
                            )

        criteria = [('%s/ID' % field_name.split('/')[0], 'LIKE', '%'), 'AND']

        dist = {}

        for entry in search_tbl.where(criteria):
            for val in entry.values():
                dist.setdefault(val, 1.0)
                dist[val] += 1

        graph = nx.Graph()
        graph.add_node(field_name)
        graph.weights = dist
        graph.weights[field_name] = 100.0

        for val in dist.keys():
            graph.add_edge(field_name, val)

        return graph

    def architecture(self):
        graph = nx.DiGraph()
        graph.add_node('projects')
        graph.labels = {'projects':'projects'}
        graph.weights = {'projects':100.0}

        def traverse(lkw, as_lkw):

            for key in schema.resources_tree[lkw]:
                as_key = '%s_%s' % (as_lkw, key)
                weight = (1 - len(as_key*2)/100.0) * 100
                graph.add_edge(as_lkw, as_key)
                graph.labels[as_key] = key
                graph.weights[as_key] = weight

                for uri in self._nomenclature.keys():
                    if uri.split('/')[-2] == key:
                        graph.add_edge(key, self._nomenclature[uri])

                traverse(key, as_key)

        traverse('projects', 'projects')

        return graph


class PaintGraph(object):
    def __init__(self, interface):
        self._intf = interface
        self.get_graph = interface._get_graph

    def architecture(self):
        graph = self.get_graph.architecture()

        plt.figure(figsize=(8,8))
        pos = nx.graphviz_layout(graph, prog='twopi', args='')

        node_size = [(float(graph.degree(v)) * 5)**3 for v in graph]
        # node_size = [graph.weights[v] ** 2 for v in graph]
        # node_color = [float(graph.degree(v)) for v in graph]
        node_color = [graph.weights[v] ** 2 for v in graph]

        nx.draw(graph, pos, labels=graph.labels, 
                node_size=node_size, node_color=node_color,
                font_size=13, font_color='orange', font_weight='bold'
                )
    
        plt.axis('off')
        plt.show()

    def experiments(self):
        graph = self.get_graph.rest_resource('experiments')
        self._draw_rest_resource(graph)

    def assessors(self):
        graph = self.get_graph.rest_resource('assessors')
        self._draw_rest_resource(graph)

    def reconstructions(self):
        graph = self.get_graph.rest_resource('reconstructions')
        self._draw_rest_resource(graph)

    def scans(self):
        graph = self.get_graph.rest_resource('scans')
        self._draw_rest_resource(graph)

    def _draw_rest_resource(self, graph):
        plt.figure(figsize=(8,8))
        pos = nx.graphviz_layout(graph, prog='twopi', args='')

        cost = lambda v: float(graph.degree(v)) ** 3 + \
            graph.weights[v] ** 2

        node_size = [cost(v) for v in graph]
        # node_size = [graph.weights[v] ** 2 for v in graph]
        # node_color = [float(graph.degree(v)) for v in graph]
        node_color = [cost(v) for v in graph]

        nx.draw(graph, pos, 
                node_size=node_size, node_color=node_color,
                font_size=13, font_color='green', font_weight='bold'
                )
    
        plt.axis('off')
        plt.show()
        
    def datatypes(self):
        graph = self.get_graph.datatypes()

        plt.figure(figsize=(8,8))
        pos = nx.graphviz_layout(graph, prog='twopi', args='')

        cost = lambda v: float(graph.degree(v)) ** 3 + \
            graph.weights[v] ** 2

        node_size = [cost(v) for v in graph]
        # node_size = [graph.weights[v] ** 2 for v in graph]
        # node_color = [float(graph.degree(v)) for v in graph]
        node_color = [cost(v) for v in graph]

        nx.draw(graph, pos, 
                node_size=node_size, node_color=node_color,
                font_size=13, font_color='green', font_weight='bold'
                )
    
        plt.axis('off')
        plt.show()

    def field_values(self, field_name):
        graph = self.get_graph.field_values(field_name)

        plt.figure(figsize=(8,8))
        pos = nx.graphviz_layout(graph, prog='twopi', args='')

        cost = lambda v: graph.weights[v]

        graph.weights[field_name] = max([cost(v) for v in graph]) / 2.0

        costs = norm_costs([cost(v) for v in graph], 10000)

        nx.draw(graph, pos, 
                node_size=costs, node_color=costs,
                font_size=13, font_color='black', font_weight='bold'
                )
    
        plt.axis('off')
        plt.show()


def norm_costs(costs, norm=1000):
    max_cost = max(costs)

    return [ (cost / max_cost) * norm for cost in costs]

    
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

        nx.draw_networkx_edges(g, pos, width=2, alpha=0.5, 
                               edge_color='black')

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

            for datatype in schema.datatypes(
                self._intf.manage.schemas._trees[xsd]):
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
            # nsmap = self._intf.manage.schemas._trees[xsd].nsmap

            if datatype_name is not None:
                datatypes = [datatype_name]
            else:
                datatypes = schema.datatypes(
                    self._intf.manage.schemas._trees[xsd]
                    )

            for datatype in datatypes:
                for path in schema.datatype_attributes(
                    self._intf.manage.schemas._trees[xsd], datatype):
                    if element_name in path:
                        paths.append(path)

        return paths

