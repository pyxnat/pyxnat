import sys
import os.path as op
import pyxnat
from . import skip_if_no_network

_modulepath = op.dirname(op.abspath(pyxnat.__file__))

dd = op.join(op.split(_modulepath)[0], 'bin')
sys.path.append(dd)

dest_project = 'testing_new'


@skip_if_no_network
def test_001_sessionmirror():
    from sessionmirror import create_parser, main
    parser = create_parser()
    cfg = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
    central = pyxnat.Interface(config=cfg)
    e = 'CENTRAL_E74609'
    args = ['--h1', cfg, '--h2', cfg, '-e', e, '-p', dest_project]
    args = parser.parse_args(args)
    main(args)
    central.array.experiments(experiment_id=e,
                              columns=['subject_label']).data[0]


@skip_if_no_network
def test_002_deletesubject():
    print('DELETING')
    cfg = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
    central = pyxnat.Interface(config=cfg)
    e = 'CENTRAL_E74609'
    e0 = central.array.experiments(experiment_id=e,
                                   columns=['subject_label', 'label']).data[0]
    subject_label = e0['subject_label']
    experiment_label = e0['label']
    e1 = central.array.experiments(project_id=dest_project,
                                   subject_label=subject_label,
                                   experiment_label=experiment_label,
                                   columns=['subject_id']).data[0]
    p = central.select.project(dest_project)
    e2 = p.subject(e1['subject_ID']).experiment(e1['ID'])
    assert(e2.exists())
    e2.delete()
    assert(not e2.exists())

