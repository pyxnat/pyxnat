import os
from uuid import uuid1
import time

from .. import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))

sid = uuid1().hex
eid = uuid1().hex

subject = central.select.project('nosetests').subject(sid)
experiment = subject.experiment(eid)

def test_fancy_resource_create():
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
    assert experiment.attrs.get('xnat:mrSessionData/age') == '42.0'

def test_attr_mget():
    time.sleep(5)
    fields = ['xnat:subjectData/investigator/firstname',
              'xnat:subjectData/investigator/lastname'
              ]

    assert subject.attrs.mget(fields) == ['john', 'doe']

def test_attr_set():
    experiment.attrs.set('xnat:mrSessionData/age', '26')
    assert experiment.attrs.get('xnat:mrSessionData/age') == '26.0'

def test_attr_mset():
    subject = central.select.project('nosetests').subject(sid)
    time.sleep(5)
    field_data = {'xnat:subjectData/investigator/firstname':'angus',
                  'xnat:subjectData/investigator/lastname':'young',
                  }

    subject.attrs.mset(field_data)
    returned = subject.attrs.mget(field_data.keys())

    assert set(returned) == \
        set(field_data.values()), '''set: %s returned: %s ''' %(field_data.values(), returned)

def test_cleanup():
    subject.delete()
    assert not subject.exists()
