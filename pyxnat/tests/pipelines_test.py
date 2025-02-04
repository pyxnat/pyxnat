import os.path as op
from pyxnat import Interface
from pyxnat.core.pipelines import PipelineNotFoundError

fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)
p = central.select.project('pyxnat_tests')


def test_pipelines_info():
    info = p.pipelines.info('DicomToNifti')
    assert (len(info) == 1)


def test_pipelines_aliases():
    aliases = p.pipelines.aliases()
    assert (aliases == {'DicomToNifti': 'DicomToNifti'})


def test_pipeline_info():
    info_keys = {'appliesTo', 'authors', 'description', 'inputParameters',
                 'path', 'resourceRequirements', 'steps', 'version'}

    pipe = p.pipelines.pipeline('DicomToNifti')
    assert (pipe.exists())

    pipe_info = pipe.info()
    assert (int(pipe_info['version']) >= 20190308)
    assert (set(pipe_info.keys()) == info_keys)


def test_pipeline_run():
    exp_id = 'BBRCDEV_E03094'

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
    exp_id = 'BBRCDEV_E03094'

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
