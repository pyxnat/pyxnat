import os
from uuid import uuid1

from .. import Interface
import os.path as op

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

#central = Interface(config='.xnat.cfg')
project = central.select.project('nosetests3')

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
