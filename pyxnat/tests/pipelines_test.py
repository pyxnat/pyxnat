import os.path as op
from pyxnat import Interface
from pyxnat.core.pipelines import PipelineNotFoundError

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)
p = central.select.project('nosetests5')


def test_pipelines_info():
    info = p.pipelines.info('DicomToNifti')
    assert (len(info) == 1)


def test_pipelines_aliases():
    aliases = p.pipelines.aliases()
    assert (aliases == {'DicomToNifti': 'DicomToNifti'})


def test_pipeline_info():
    info_keys = ['appliesTo', 'authors', 'description',
                 'inputParameters', 'path', 'steps', 'version']

    pipe = p.pipelines.pipeline('DicomToNifti')
    assert (pipe.exists())

    pipe_info = pipe.info()
    assert (int(pipe_info['version']) >= 20150114)
    assert (sorted(pipe_info.keys()) == info_keys)


def test_pipeline_run():
    exp_id = 'CENTRAL02_E01603'

    try:
        wrong_pipe = p.pipelines.pipeline('INVALID_PIPELINE')
        wrong_pipe.run(exp_id)
    except PipelineNotFoundError as pe:
        print(pe)

    try:
        pipe = p.pipelines.pipeline('DicomToNifti')
        pipe.run('INVALID_EXP')
    except ValueError as ve:
        print(ve)

    pipe = p.pipelines.pipeline('DicomToNifti')
    pipe.run(exp_id)


def test_pipeline_status():
    exp_id = 'CENTRAL02_E01603'

    try:
        wrong_pipe = p.pipelines.pipeline('INVALID_PIPELINE')
        wrong_pipe.status(exp_id)
    except PipelineNotFoundError as pe:
        print(pe)

    try:
        pipe = p.pipelines.pipeline('DicomToNifti')
        pipe.status('INVALID_EXP')
    except ValueError as ve:
        print(ve)

    pipe = p.pipelines.pipeline('DicomToNifti')
    status = pipe.status(exp_id)
    assert (isinstance(status, dict))
    assert (status['status'] != 'Failed')
