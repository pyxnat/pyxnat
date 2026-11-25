import os.path as op
from uuid import uuid1
import time
from pyxnat.tests import skip_if_no_network
from pyxnat import Interface
from pyxnat.core import interfaces


fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)
interfaces.STUBBORN = True

sid = uuid1().hex
eid = uuid1().hex

subject = central.select.project('pyxnat_tests').subject(sid)
experiment = subject.experiment(eid)


@skip_if_no_network
def test_01_fancy_resource_create():

    field_data = {'experiment': 'xnat:mrSessionData',
                  'ID': 'TEST_%s' % eid,
                  'xnat:mrSessionData/age': '42',
                  'xnat:subjectData/investigator/lastname': 'doe',
                  'xnat:subjectData/investigator/firstname': 'john',
                  'xnat:subjectData/ID': 'TEST_%s' % sid,
                  }

    experiment.create(**field_data)
    assert subject.exists()
    assert experiment.exists()

    globals()['subject'] = experiment.parent()
    globals()['experiment'] = experiment


@skip_if_no_network
def test_02_attr_get():
    assert experiment.attrs.get('xnat:mrSessionData/age') == '42.0'


@skip_if_no_network
def test_03_attr_mget():
    time.sleep(5)
    fields = ['xnat:subjectData/investigator/firstname',
              'xnat:subjectData/investigator/lastname'
              ]

    assert subject.attrs.mget(fields) == ['john', 'doe']


@skip_if_no_network
def test_04_attr_set():
    experiment.attrs.set('xnat:mrSessionData/age', '26')
    assert experiment.attrs.get('xnat:mrSessionData/age') == '26.0'

# def test_attr_mset():
#     subject = central.select.project('nosetests').subject(sid)
#     time.sleep(5)
#     field_data = {'xnat:subjectData/investigator/firstname':'angus',
#                   'xnat:subjectData/investigator/lastname':'young',
#                   }
#
#     subject.attrs.mset(field_data)
#     returned = subject.attrs.mget(field_data.keys())
#
#     assert set(returned) == \
#         set(field_data.values()),
#              '''set: %s returned: %s ''' %(field_data.values(), returned)


@skip_if_no_network
def test_05_cleanup():

    subject.delete()
    assert not subject.exists()


@skip_if_no_network
def test_06_list_project_attrs():

    project_attributes = ['xnat:projectData/name',
                          'xnat:projectData/type',
                          'xnat:projectData/description',
                          'xnat:projectData/keywords',
                          'xnat:projectData/aliases',
                          'xnat:projectData/aliases/alias',
                          'xnat:projectData/aliases/alias/None',
                          'xnat:projectData/publications',
                          'xnat:projectData/publications/publication',
                          'xnat:projectData/resources',
                          'xnat:projectData/resources/resource',
                          'xnat:projectData/studyProtocol',
                          'xnat:projectData/PI',
                          'xnat:projectData/investigators',
                          'xnat:projectData/investigators/investigator',
                          'xnat:projectData/fields',
                          'xnat:projectData/fields/field',
                          'xnat:projectData/fields/field/None']

    p = central.select.project('pyxnat_tests')
    assert p.attrs() == []

    central.manage.schemas.add('xapi/schemas/xnat')
    p = central.select.project('pyxnat_tests')
    assert p.attrs() == project_attributes
