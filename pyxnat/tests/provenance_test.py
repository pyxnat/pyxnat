from uuid import uuid1
from . import skip_if_no_network
from .. import Interface
import os.path as op
import os

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))
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


@skip_if_no_network
def test_provenance():
    assessor = project.subject(sid).experiment(eid).assessor(
        aid).insert(use_label=True)
    assert assessor.exists()
    assessor.provenance.set(prov)
    _prov = assessor.provenance.get()[0]

    assert prov['program'] == _prov['program'], "Subject: %s Study: %s Prov: %s" % (sid, eid, aid)

# def test_del_provenance():
#     assessor.provenance.delete()
#     print assessor.provenance.get()
#     assert assessor.provenance.get()[0] == []

@skip_if_no_network
def test_provenance_cleanup():
    project.subject(sid).delete()
    assert not project.subject(sid).exists()
