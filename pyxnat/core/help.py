try:
    import networkx as nx
    from networkx.drawing.nx_agraph import graphviz_layout
    import matplotlib.pyplot as plt
    _DRAW_GRAPHS = True
except Exception:
    _DRAW_GRAPHS = False

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
            interface:
                :class:`Interface` Object
        """
        self._intf = interface
        self._get_json = interface._get_json
        self._auto = True
        self._tick = 30

        self.schemas = SchemasInspector(interface)

    def __call__(self):
        for name in ['experiment', 'assessor', 'scan', 'reconstruction']:
            self._resource_struct(name)

    def set_autolearn(self, auto=None, tick=None):
        """ Once in a while queries will persist additional
            information on the server. This information is available
            through the following methods of this class:

                - experiment_types
                - assessor_types
                - scan_types
                - reconstruction_types

            It is also transparently used in insert operations.

            Parameters
            ----------
            auto: boolean
                True to enable auto learn. False to disable.
            tick: int
                Every 'tick' seconds, if a query is issued, additional
                information will be persisted.

            See Also
            --------
            :func:`EObject.insert`
        """
        if auto is not None:
            self._auto = auto
        if tick is not None:
            self._tick = tick

    def datatypes(self, pattern='*', fields_pattern=None):
        """ Discovers the datatypes and datafields of the database.

            Parameters
            ----------
            pattern: string
                Pattern for the datatype. May include wildcards.
            fields_pattern: string
                - Pattern for the datafields -- may include wildcards.
                - If specified, datafields will be returned instead of
                  datatypes.

            Returns
            -------
            list : datatypes or datafields depending on the argument usage.
        """
        self._intf._get_entry_point()

        search_els = self._get_json('%s/search/elements?format=json' %
                                    self._intf._get_entry_point())

        if not fields_pattern and ('*' in pattern or '?' in pattern):
            return get_column(search_els, 'ELEMENT_NAME', pattern)

        else:
            fields = []
            for datatype in get_column(search_els, 'ELEMENT_NAME', pattern):
                df = self._datafields(datatype, fields_pattern or '*', True)
                fields.extend(df)

            return fields

    def _datafields(self, datatype, pattern='*', prepend_type=True):
        self._intf._get_entry_point()

        search_fds = self._get_json('%s/search/elements/%s?format=json' %
                                    (self._intf._get_entry_point(),
                                        datatype))

        fields = get_column(search_fds, 'FIELD_ID', pattern)

        return ['%s/%s' % (datatype, field)
                if prepend_type else field
                for field in fields
                if '=' not in field and 'SHARINGSHAREPROJECT' not in field
                ]

    def experiment_types(self):
        """ Returns the datatypes used at the experiment level in this
            database.

            See Also
            --------
            :func:`Inspector.set_autolearn`
        """
        return self._resource_types('experiment')

    def assessor_types(self):
        """ Returns the datatypes used at the assessor level in this
            database.

            See Also
            --------
            :func:`Inspector.set_autolearn`
        """
        return self._resource_types('assessor')

    def reconstruction_types(self):
        """ Returns the datatypes used at the reconstruction level in this
            database.

            See Also
            --------
            :func:`Inspector.set_autolearn`
        """
        return self._resource_types('reconstruction')

    def scan_types(self):
        """ Returns the datatypes used at the scan level in this
            database.

            See Also
            --------
            :func:`Inspector.set_autolearn`
        """
        return self._resource_types('scan')

    def field_values(self, field_name):
        """ Look for the values a specific datafield takes in the database.
        """
        self._intf._get_entry_point()

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
        """ Look for the values a the project level in the database.

            .. note::
                Is equivalent to interface.select.projects().get()
        """
        self._intf._get_entry_point()

        return get_column(self._get_json(
                '%s/projects' % self._intf._entry), 'ID')

    def subject_values(self, project=None):
        """ Look for the values a the subject level in the database.

            .. note::
                Is equivalent to interface.select('//subjects').get()
        """
        self._intf._get_entry_point()

        uri = '%s/subjects?columns=ID' % self._intf._entry

        if project is not None:
            uri += '&project=%s' % project

        return get_column(self._get_json(uri), 'ID')

    def experiment_values(self, datatype, project=None):
        """ Look for the values a the experiment level for a given datatype
            in the database.

            .. note::
                The  datatype should be one of Inspector.experiment_types()

            Parameters
            ----------
            datatype: string
                An experiment type. eg: xnat:mrsessiondata
            project: string
                Optional. Restrict operation to a project.
        """
        self._intf._get_entry_point()

        uri = '%s/experiments?columns=ID' % self._intf._entry
        if datatype is not None:
            uri += '&xsiType=%s' % datatype
        if project is not None:
            uri += '&project=%s' % project

        return get_column(self._get_json(uri), 'ID')

    def assessor_values(self, experiment_type, project=None):
        """ Look for the values at the assessor level for a given experiment
            type in the database.

            .. note::
               The experiment type should be one of
               Inspector.experiment_types()

            .. warning::
                Depending on the number of elements the operation may
                take a while.

            Parameters
            ----------
            datatype: string
                An experiment type. eg: xnat:mrsessiondata
            project: string
                Optional. Restrict operation to a project.
        """
        return self._sub_experiment_values('assessor',
                                           project, experiment_type)

    def scan_values(self, experiment_type, project=None):
        """ Look for the values at the scan level for a given experiment
            type in the database.

            .. note::
               The experiment type should be one of
               Inspector.experiment_types()

            .. warning::
                Depending on the number of elements the operation may
                take a while.

            Parameters
            ----------
            datatype: string
                An experiment type.
            project: string
                Optional. Restrict operation to a project.
        """
        return self._sub_experiment_values('scan', project, experiment_type)

    def reconstruction_values(self, experiment_type, project=None):
        """ Look for the values at the reconstruction level for a given
            experiment type in the database.

            .. note::
               The experiment type should be one of
               Inspector.experiment_types()

            .. warning::
                Depending on the number of elements the operation may
                take a while.

            Parameters
            ----------
            datatype: string
                An experiment type.
            project: string
                Optional. Restrict operation to a project.
        """
        return self._sub_experiment_values('reconstruction',
                                           project, experiment_type)

    def structure(self):
        """ Displays the keywords structure used in XNAT REST API.
        """
        def traverse(coll, lvl):
            for key in schema.resources_tree[coll]:
                print('%s+%s' % (' ' * lvl, key.upper()))

                datatypes = set([
                        self._intf._struct[uri]
                        for uri in self._intf._struct.keys()
                        if uri.split('/')[-2] == key
                        ])

                if datatypes != set():
                    print('%s  %s' % (' ' * lvl, '-' * len(key)))

                for datatype in datatypes:
                    print('%s- %s' % (' ' * lvl, datatype))

                if key in schema.resources_tree.keys():
                    traverse(key, lvl + 4)

        print('- %s' % 'PROJECTS')
        traverse('projects', 4)

    def _sub_experiment_values(self, sub_exp, project, experiment_type):
        self._intf._get_entry_point()

        values = []

        column = '%s/%ss/%s/id' % \
            (experiment_type.lower(), sub_exp, sub_exp)

        sub_exps = '%s/experiments?columns=ID,%s' % (self._intf._entry,
                                                     column
                                                     )

        if project is not None:
            sub_exps += '&project=%s' % project

        values = get_column(self._get_json(sub_exps), column)

        return list(set(values))

    def _resource_struct(self, name):

        return self._intf._struct

    def _resource_types(self, name):
        return list(set(self._resource_struct(name).values()))


class GraphData(object):
    def __init__(self, interface):
        self._intf = interface
        self._struct = interface._struct

    # def link(self, subjects, fields):

    #     criteria = [('xnat:subjectData/SUBJECT_ID', '=', _id)
    #                 for _id in subjects
    #                 ]
    #     criteria += ['OR']
    #     # variables = ['xnat:subjectData/SUBJECT_ID'] + fields

    #     subject_id = 'xnat:subjectData/SUBJECT_ID'

    #     for field in fields:

    #         field_tbl = self._intf.select('xnat:subjectData',
    #                                       [subject_id, field]
    #                                       ).where(criteria)
    #         head = field_tbl.headers()
    #         head.remove('subject_id')
    #         head = head[0]
    #         possible = set(field_tbl.get(head))

    #         groups = {}

    #         for val in possible:
    #             groups[val] = field_tbl.where(**{head:val}
    #                                             ).select('subject_id')

    #     return groups

    def datatypes(self, pattern='*'):
        graph = nx.DiGraph()
        graph.add_node('datatypes')
        graph.labels = {'datatypes': 'datatypes'}
        graph.weights = {'datatypes': 100.0}

        datatypes = self._intf.inspect.datatypes(pattern)
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
        resource_types = self._intf.inspect._resource_types(name)

        graph = nx.DiGraph()
        graph.add_node(name)
        graph.labels = {name: name}
        graph.weights = {name: 100.0}

        namespaces = set([exp.split(':')[0] for exp in resource_types])

        for ns in namespaces:
            graph.add_edge(name, ns)
            graph.weights[ns] = 70.0

            for exp in resource_types:
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

    def architecture(self, with_datatypes=True):
        graph = nx.DiGraph()
        graph.add_node('projects')
        graph.labels = {'projects': 'projects'}
        graph.weights = {'projects': 100.0}

        def traverse(lkw, as_lkw):

            for key in schema.resources_tree[lkw]:
                as_key = '%s_%s' % (as_lkw, key)
                weight = (1 - len(as_key*2)/100.0) * 100
                graph.add_edge(as_lkw, as_key)
                graph.labels[as_key] = key
                graph.weights[as_key] = weight

                if with_datatypes:
                    for uri in self._struct.keys():
                        if uri.split('/')[-2] == key:
                            datatype = self._struct[uri]
                            graph.add_edge(as_key, datatype)
                            graph.weights[datatype] = 10
                            graph.labels[datatype] = datatype

                traverse(key, as_key)

        traverse('projects', 'projects')

        return graph


class PaintGraph(object):
    def __init__(self, interface):
        self._intf = interface
        self.get_graph = interface._get_graph

    def architecture(self, with_datatypes=True, save=None):
        graph = self.get_graph.architecture(with_datatypes)

        plt.figure(figsize=(8, 8))
        pos = graphviz_layout(graph, prog='twopi', args='')

        # node_size = [(float(graph.degree(v)) * 5)**3 for v in graph]
        # node_size = [graph.weights[v] ** 2 for v in graph]
        # node_color = [float(graph.degree(v)) for v in graph]
        # node_color = [graph.weights[v] ** 2 for v in graph]

        cost = lambda v: float(graph.degree(v)) ** 3 + \
            graph.weights[v] ** 2

        costs = norm_costs([cost(v) for v in graph], 10000)

        nx.draw(graph, pos, labels=graph.labels,
                node_size=costs, node_color=costs,
                font_size=13, font_color='orange',
                font_weight='bold', with_labels=True
                )

        plt.axis('off')

        if save is not None:
            plt.savefig(save)

        plt.show()

    def experiments(self, save=None):
        graph = self.get_graph.rest_resource('experiments')
        self._draw_rest_resource(graph, save=None)

    def assessors(self, save=None):
        graph = self.get_graph.rest_resource('assessors')
        self._draw_rest_resource(graph, save=None)

    def reconstructions(self, save=None):
        graph = self.get_graph.rest_resource('reconstructions')
        self._draw_rest_resource(graph, save=None)

    def scans(self):
        graph = self.get_graph.rest_resource('scans')
        self._draw_rest_resource(graph)

    def _draw_rest_resource(self, graph, save=None):
        plt.figure(figsize=(8, 8))
        pos = graphviz_layout(graph, prog='twopi', args='')

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

        if save is not None:
            plt.savefig(save)

        plt.show()

    def datatypes(self, pattern='*', save=None):
        graph = self.get_graph.datatypes(pattern)

        plt.figure(figsize=(8, 8))
        pos = graphviz_layout(graph, prog='twopi', args='')

        cost = lambda v: float(graph.degree(v)) ** 3 + \
            graph.weights[v] ** 2

        node_size = [cost(v) for v in graph]
        # node_size = [graph.weights[v] ** 2 for v in graph]
        # node_color = [float(graph.degree(v)) for v in graph]
        node_color = [cost(v) for v in graph]

        nx.draw(graph, pos,
                node_size=node_size, node_color=node_color,
                font_size=13, font_color='green', font_weight='bold',
                with_labels=True
                )

        plt.axis('off')

        if save is not None:
            plt.savefig(save)

        plt.show()

    def field_values(self, field_name, save=None):
        graph = self.get_graph.field_values(field_name)

        plt.figure(figsize=(8, 8))
        pos = graphviz_layout(graph, prog='twopi', args='')

        cost = lambda v: graph.weights[v]

        graph.weights[field_name] = max([cost(v) for v in graph]) / 2.0

        costs = norm_costs([cost(v) for v in graph], 10000)

        nx.draw(graph, pos,
                node_size=costs, node_color=costs,
                font_size=13, font_color='black',
                font_weight='bold', with_labels=True
                )

        plt.axis('off')

        if save is not None:
            plt.savefig(save)

        plt.show()


def norm_costs(costs, norm=1000):
    max_cost = max(costs)

    return [(cost / max_cost) * norm for cost in costs]


# class GraphDrawer(object):
#     def __init__(self, interface):
#         self._intf = interface

#     def datatypes(self, project):
#         self._intf.connection.set_strategy('offline')

#         experiments_types = self._intf.inspect.datatypes.experiments(project)

#         labels = {project:project, 'Experiments':'Experiments'}

#         g = nx.Graph()

#         g.add_edge(project, 'Experiments', {'weight':1})

#         for exp_type in experiments_types:
#             g.add_edge('Experiments', exp_type, {'weight':8})
#             labels[exp_type] = exp_type

#         pos = nx.graphviz_layout(g, prog='twopi', args='')

#         nx.draw_networkx_nodes(g, pos,
#                                nodelist=[project],
#                                node_color='green', alpha=0.7,
#                                node_size=2500, node_shape='s')

#         nx.draw_networkx_nodes(g, pos,
#                                nodelist=['Experiments'],
#                                node_color='blue', alpha=0.7,
#                                node_size=2000, node_shape='p')

#         nx.draw_networkx_nodes(g, pos,
#                                nodelist=experiments_types,
#                                node_color='red', alpha=0.7,
#                                node_size=1500, node_shape='o')

#         nx.draw_networkx_edges(g, pos, width=2, alpha=0.5,
#                                edge_color='black')

#         nx.draw_networkx_labels(g, pos, labels,
#                                 alpha=0.9, font_size=8,
#                                 font_color='black', font_weight='bold')

#         plt.axis('off')
#         plt.show()

#         self._intf.connection.revert_strategy()

class SchemasInspector(object):
    def __init__(self, interface):
        self._intf = interface

    def __call__(self):
        self._intf.manage.schemas()

        for xsd in self._intf.manage.schemas():
            print('-'*40)
            print(xsd.upper())
            print('-'*40)
            print()

            trees = self._intf.manage.schemas._trees[xsd]
            for datatype in schema.datatypes(trees):
                print('[%s]' % datatype)
                print()

                for path in schema.datatype_attributes(trees, datatype):
                    print(path)

                print()

    def look_for(self, element_name, datatype_name=None):
        paths = []
        self._intf.manage.schemas._init()

        if ':' in element_name:
            for root in self._intf.manage.schemas._trees.values():
                paths.extend(schema.datatype_attributes(root, element_name))
            return paths

        for xsd in self._intf.manage.schemas():
            # nsmap = self._intf.manage.schemas._trees[xsd].nsmap
            trees = self._intf.manage.schemas._trees[xsd]
            if datatype_name is not None:
                datatypes = [datatype_name]
            else:
                datatypes = schema.datatypes(trees)

            for datatype in datatypes:
                for path in schema.datatype_attributes(trees, datatype):
                    if element_name in path:
                        paths.append(path)

        return paths
