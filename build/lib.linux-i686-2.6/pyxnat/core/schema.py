
# REST collection resources tree
resources_tree = {'projects':['subjects', 'resources'],
            'subjects':['experiments', 'resources'],
            'experiments':['assessors', 'reconstructions', 'scans', 
                           'resources'],
            'assessors':['resources','in_resources','out_resources'],
            'reconstructions':['in_resources','out_resources'],
            'scans':['resources'],
            'resources':['files'],
            'files':[],
            'in_resources':['files'],
            'in_files':[],
            'out_resources':['files'],
            'out_files':[],
            }

# REST resources that are not natively supported
extra_resources_tree = {'projects':['assessors', 'scans', 'reconstructions'],
            'subjects':['assessors', 'scans', 'reconstructions'],
            }

# REST <Python to URI> translation table 
rest_translation = {'in_resources':'in/resources',
                    'in_files':'in/files',
                    'out_resources':'out/resources',
                    'out_files':'out/files',
                    'in_resource':'in/resource',
                    'in_file':'in/file',
                    'out_resource':'out/resource',
                    'out_file':'out/file',
                    }

# REST json format <id_header, label_header>
json = {'projects':['ID', 'ID'],
        'subjects':['ID', 'label'],
        'experiments':['ID', 'label'],
        'assessors':['ID', 'label'],
        'reconstructions':['ID', 'label'],
        'scans':['ID', 'label'],
        'resources':['xnat_abstractresource_id', 'label'],
        'out_resources':['xnat_abstractresource_id', 'label'],
        'in_resources':['xnat_abstractresource_id', 'label'],
        'files':['Name', 'Name'],
        }

resources_singular = [key.rsplit('s', 1)[0] for key in resources_tree.keys()]
resources_plural   = resources_tree.keys()
resources_types    = resources_singular + resources_plural

default_datatypes = {'projects':'xnat:projectData',
                     'subjects':'xnat:subjectData',
                     'experiments':'xnat:mrSessionData',
                     'assessors':'xnat:imageAssessorData',
                     'reconstructions':None,
                     'scans':'xnat:mrScanData',
                     'resources':None,
                     'in_resources':None,
                     'out_resources':None,
                     }

