import sys
import os.path as op
import pyxnat
from pyxnat.tests import skip_if_no_network

_modulepath = op.dirname(op.abspath(pyxnat.__file__))
dd = op.join(op.split(_modulepath)[0], 'bin')
sys.path.append(dd)

cfg = op.abspath('.devxnat.cfg')
central = pyxnat.Interface(config=cfg)

src_project = 'pyxnat_tests'
dest_project = 'pyxnat_tests2'


@skip_if_no_network
def test_001_sessionmirror():
    from sessionmirror import create_parser, main, subj_compare
    e = 'BBRCDEV_E03099'
    parser = create_parser()
    args = ['--h1', cfg, '--h2', cfg, '-e', e, '-p', dest_project]
    args = parser.parse_args(args)
    main(args)

    cols = ['label', 'subject_label']
    data = central.array.experiments(experiment_id=e, columns=cols).data[0]
    s1 = central.select.project(src_project).subject(data['subject_label'])
    s2 = central.select.project(dest_project).subject(data['subject_label'])
    assert (subj_compare(s1, s2) == 0)


@skip_if_no_network
def test_002_delete_experiment():
    print('DELETING')
    e = 'BBRCDEV_E03099'
    cols = ['subject_label', 'label']
    e0 = central.array.experiments(experiment_id=e, columns=cols).data[0]
    subject_label = e0['subject_label']
    experiment_label = e0['label']
    e1 = central.array.experiments(project_id=dest_project,
                                   subject_label=subject_label,
                                   experiment_label=experiment_label,
                                   columns=['subject_id']).data[0]
    p = central.select.project(dest_project)
    e2 = p.subject(e1['subject_ID']).experiment(e1['ID'])
    assert (e2.exists())
    e2.delete()
    assert (not e2.exists())

