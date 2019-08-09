import os
import os.path as op
from uuid import uuid1
import time
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest
from .. import Interface

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))
from pyxnat.core import interfaces
interfaces.STUBBORN = True

sid = uuid1().hex
eid = uuid1().hex

subject = central.select.project('nosetests3').subject(sid)
experiment = subject.experiment(eid)


def test_fancy_resource_create():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

    field_data = {'experiment':'xnat:mrSessionData',
                  'ID':'TEST_%s' % eid,
                  'xnat:mrSessionData/age':'42',
                  'xnat:subjectData/investigator/lastname':'doe',
                  'xnat:subjectData/investigator/firstname':'john',
                  'xnat:subjectData/ID': 'TEST_%s' % sid,
                  }

    experiment.create(**field_data)
    assert subject.exists()
    assert experiment.exists()

    globals()['subject'] = experiment.parent()
    globals()['experiment'] = experiment

def test_attr_get():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

    assert experiment.attrs.get('xnat:mrSessionData/age') == '42.0'

def test_attr_mget():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

    time.sleep(5)
    fields = ['xnat:subjectData/investigator/firstname',
              'xnat:subjectData/investigator/lastname'
              ]

    assert subject.attrs.mget(fields) == ['john', 'doe']

def test_attr_set():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

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
#         set(field_data.values()), '''set: %s returned: %s ''' %(field_data.values(), returned)

def test_cleanup():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

    subject.delete()
    assert not subject.exists()

def test_list_project_attrs():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')

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

    p = central.select.project('nosetests')
    assert(p.attrs() == [])

    central.manage.schemas.add('xapi/schemas/xnat')
    p = central.select.project('nosetests')
    assert (p.attrs() == project_attributes)
