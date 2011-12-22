import os
from uuid import uuid1

from .. import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface('https://central.xnat.org', 'nosetests', 'nosetests')

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
    fields = ['xnat:subjectData/investigator/firstname', 
              'xnat:subjectData/investigator/lastname'
              ]

    assert subject.attrs.mget(fields) == ['john', 'doe']

def test_attr_set():
    experiment.attrs.set('xnat:mrSessionData/age', '26')
    assert experiment.attrs.get('xnat:mrSessionData/age') == '26.0'

def test_attr_mset():
    field_data = {'xnat:subjectData/investigator/firstname':'angus',
                  'xnat:subjectData/investigator/lastname':'young',
                  }

    subject.attrs.mset(field_data)

    assert set(subject.attrs.mget(field_data.keys())) == \
        set(field_data.values())

def test_cleanup():
    subject.delete()
    assert not subject.exists()
