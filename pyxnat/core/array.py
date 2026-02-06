from .jsonutil import JsonTable


class ArrayData(object):

    def __init__(self, interface):
        self._intf = interface

    def _get_array(self, query_string, project_id=None,
                   subject_id=None, subject_label=None,
                   experiment_id=None, experiment_label=None,
                   experiment_type='xnat:subjectAssessorData',
                   columns=None, constraints=None
                   ):

        if constraints is None:
            constraints = {}

        uri = '%s/experiments?xsiType=%s' % (self._intf._get_entry_point(),
                                             experiment_type)

        if project_id is not None:
            uri += '&project=%s' % project_id

        if subject_id is not None:
            uri += '&%s/subject_id=%s' % (experiment_type, subject_id)

        # Subject Label is only held in the xnat:subjectData so look for it
        # there. This should join against whatever the experiment type is.
        if subject_label is not None:
            uri += '&xnat:subjectData/label=%s' % (subject_label)

        if experiment_id is not None:
            uri += '&ID=%s' % experiment_id

        if experiment_label is not None:
            uri += '&label=%s' % experiment_label

        uri += query_string

        if constraints != {}:
            uri += ',' + ','.join(constraints.keys())

        if columns is not None:
            uri += ',' + ','.join(columns)

        c = {}

        [c.setdefault(key.lower(), value)
         for key, value in constraints.items()
         ]

        return JsonTable(self._intf._get_json(uri)).where(**c)

    def experiments(self, project_id=None, subject_id=None, subject_label=None,
                    experiment_id=None, experiment_label=None,
                    experiment_type='xnat:subjectAssessorData',
                    columns=None,
                    constraints=None):

        """ Returns a list of all visible experiment IDs of the specified
            type, filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_id: string
                Name pattern to filter by experiment ID.
            experiment_label: string
                Name pattern to filter by experiment ID.
            experiment_type: string
                xsi path type; e.g. 'xnat:mrSessionData'
            columns: list
                Values to return.
            constraints: dict
                Dictionary of xsi_type (key--) and parameter (--value)
                pairs by which to filter.
            """

        query_string = '&columns=ID,project,%s/subject_id' % experiment_type

        return self._get_array(query_string, project_id,
                               subject_id, subject_label,
                               experiment_id, experiment_label,
                               experiment_type, columns, constraints
                               )

    def mrsessions(self, project_id=None, subject_id=None, subject_label=None,
                   experiment_id=None, experiment_label=None,
                   columns=None,
                   constraints=None):

        """ Returns a list of all MR sessions, filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_id: string
                Name pattern to filter by experiment ID.
            experiment_label: string
                Name pattern to filter by experiment ID.
            columns: list
                Values to return.
            constraints: dict
                Dictionary of xsi_type (key--) and parameter (--value)
                pairs by which to filter.
            """

        return self.experiments(project_id, subject_id, subject_label,
                                experiment_id, experiment_label,
                                'xnat:mrSessionData', columns, constraints
                                )

    def scans(self, project_id=None, subject_id=None, subject_label=None,
              experiment_id=None, experiment_label=None,
              experiment_type='xnat:imageSessionData',
              scan_type='xnat:imageScanData',
              columns=None,
              constraints=None
              ):

        """ Returns a list of all visible scan IDs of the specified type,
            filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_id: string
                Name pattern to filter by experiment ID.
            experiment_label: string
                Name pattern to filter by experiment ID.
            experiment_type: string
                xsi path type; e.g. 'xnat:mrSessionData'
            scan_type: string
                xsi path type; e.g. 'xnat:mrScanData', etc.
            columns: list
                Values to return.
            constraints: dict
                Dictionary of xsi_type (key--) and parameter (--value)
                pairs by which to filter.
            """

        query_string = '&columns=ID,project,%s/subject_id,%s/ID' % (
            experiment_type, scan_type)

        array = self._get_array(query_string, project_id,
                                subject_id, subject_label,
                                experiment_id, experiment_label,
                                experiment_type, columns, constraints)
        id_key = ('%s/ID' % scan_type).lower()
        return JsonTable([i for i in array if i[id_key]])

    def mrscans(self, project_id=None, subject_id=None, subject_label=None,
                experiment_id=None, experiment_label=None,
                columns=None,
                constraints=None):

        """ Returns a list of all MR scans, filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_id: string
                Name pattern to filter by experiment ID.
            experiment_label: string
                Name pattern to filter by experiment ID.
            columns: list
                Values to return.
            constraints: dict
                Dictionary of xsi_type (key--) and parameter (--value)
                pairs by which to filter.
            """

        return self.scans(project_id, subject_id, subject_label,
                          experiment_id, experiment_label,
                          'xnat:mrSessionData', 'xnat:mrScanData',
                          columns, constraints
                          )

    def search_experiments(self,
                           project_id=None,
                           subject_id=None,
                           subject_label=None,
                           experiment_type='xnat:subjectAssessorData',
                           columns=None,
                           constraints=None
                           ):

        """ Returns a list of all visible experiment IDs of the
            specified type, filtered by optional constraints. This
            function is a shortcut using the search engine.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_type: string
                xsi path type must be a leaf session type.
                defaults to 'xnat:mrSessionData'
            columns: List[string]
                list of xsi paths for names of columns to return.
            constraints: list[(tupple)]
                List of tupples for comparison in the form (key, comparison,
                value) valid comparisons are: =, <, <=,>,>=, LIKE
            """

        if columns is None:
            columns = []

        where_clause = []

        if project_id is not None:
            item = ('%s/project' % experiment_type, "=", project_id)
            where_clause.append(item)
        if subject_id is not None:
            where_clause.append(('xnat:subjectData/ID', "=", subject_id))
        if subject_label is not None:
            where_clause.append(('xnat:subjectData/LABEL', "=", subject_label))

        if constraints is not None:
            where_clause.extend(constraints)

        if where_clause != []:
            where_clause.append('AND')

        if where_clause != []:
            sel = self._intf.select(experiment_type, columns=columns)
            table = sel.where(where_clause)
            return table
        else:
            table = self._intf.select(experiment_type, columns=columns)
            return table.all()
