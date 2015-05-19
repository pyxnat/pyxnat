import os
from uuid import uuid1

from .. import Interface

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))
project = central.select('/project/nosetests')

prov = {
    'program':'young',
    'timestamp':'2011-03-01T12:01:01.897987', 
    'user':'angus', 
    'machine':'war', 
    'platform':'linux',
    }

sid = uuid1().hex
eid = uuid1().hex
aid = uuid1().hex

assessor = project.subject(sid).experiment(eid).assessor(
    aid).insert(use_label=True)


def test_provenance():
    assert assessor.exists()
    assessor.provenance.set(prov)
    _prov = assessor.provenance.get()[0]

    assert prov['program'] == _prov['program'], "Subject: %s Study: %s Prov: %s" % (sid, eid, aid)

# def test_del_provenance():
#     assessor.provenance.delete()
#     print assessor.provenance.get()
#     assert assessor.provenance.get()[0] == []

def test_provenance_cleanup():
    project.subject(sid).delete()
    assert not project.subject(sid).exists()
