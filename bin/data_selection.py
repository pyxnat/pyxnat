#! /usr/bin/env python
import sys
import os.path as op
import logging as log
import pyxnat


project_description = 'Automatically generated project hosting a ' \
                      'selection of existing data for sharing ' \
                      'purposes. This is not a real study.'


def generate_project_id(label):
    """Helper for the generation of a synthetic XNAT project name."""

    from datetime import datetime
    now = datetime.now()  # current date and time

    timestamp = now.strftime("%Y%m%d")
    project_id = ('_{}_{}'.format(label, timestamp))
    return project_id


def create_project(intf, project_name):
    """Create an XNAT project setting by-default attributes."""

    p = intf.select.project(project_name)
    if p.exists():
        log.error('Project `{}` already exists. Aborting.'.format(project_name))
        sys.exit(1)

    log.info('Creating project `{}`...'.format(project_name))
    p.create()
    p.set_accessibility('protected')
    p.set_prearchive_code('4')
    p.attrs.set('description', project_description)
    p.attrs.set('keywords', 'data_selection')

    return p


def mirror_session(src_sess, dst_sess, cache_dir, scan_types=None, res_types=None):
    """Mirror XNAT session from source to destination."""

    from sessionmirror import write_xml, copy_attributes, copy_scan, copy_res

    # Write xml to file
    sess_xml = src_sess.get()
    xml_path = op.join(cache_dir, 'sess.xml')
    write_xml(sess_xml, xml_path)

    # copy metadata (xml) to mirrored experiment
    sess_type = src_sess.datatype()
    log.info('Creating experiment `{}`...'.format(dst_sess._urn))
    dst_sess.create(experiments=sess_type)
    copy_attributes(src_sess, dst_sess)

    # filter scan types to be exported (if applies)
    scans = list(src_sess.scans())
    if scan_types:
        scans_filtered = [s for s in scans if s.attrs.get('type') in scan_types]
        scans = scans_filtered

    if scans:
        # process each scan
        for scan in scans:
            scan_label = scan.label()
            log.info('Processing scan `{}`...'.format(scan_label))
            dst_scan = dst_sess.scan(scan_label)
            scan_cache_dir = op.join(cache_dir, scan_label)
            copy_scan(scan, dst_scan, scan_cache_dir)

    # filter resources to be exported (if applies)
    resources = list(src_sess.resources())
    if res_types:
        res_filtered = [r for r in resources if r.label() in res_types]
        resources = res_filtered

    if resources:
        # process each resource
        for res in resources:
            res_label = res.label()
            log.info('Processing resource `{}`...'.format(res_label))
            dst_res = dst_sess.resource(res_label)
            res_cache_dir = op.join(cache_dir, res_label)
            copy_res(res, dst_res, res_cache_dir, use_zip=True)

    return dst_sess


def main(args):

    import pandas as pd
    import tempfile
    from shutil import rmtree

    c1 = pyxnat.Interface(config=args.source_config)
    log.info('Source XNAT server: `{}`'.format(c1.head('').url))
    c2 = c1
    if args.dest_config:
        c2 = pyxnat.Interface(config=args.dest_config)
    log.info('Destination XNAT server: `{}`'.format(c2.head('').url))

    exps = list(pd.read_csv(args.selection_list)['ID'])

    scans = None
    if args.scans:
        scans = args.scans.split(',')
        log.info('Selected scans: {}'.format(scans))

    res = None
    if args.resources:
        res = args.resources.split(',')
        log.info('Selected resources: {}'.format(res))

    # create a project for the data selection
    proj = generate_project_id(args.label)
    if args.reuse_project:
        log.info('Reusing project `{}`'.format(proj))
        p = c2.select.project(proj)
        if not p.exists():
            log.error('Project `{}` not found. Aborting.'.format(proj))
            sys.exit(1)
    else:
        p = create_project(c2, proj)

    # mirror experiments
    for experiment_id in exps:
        e = c1.array.experiments(experiment_id=experiment_id,
                                 columns=['subject_label', 'label']).data[0]
        s = p.subject(e['subject_label'])
        if not s.exists():
            log.info('Creating subject `{}`...'.format(e['subject_label']))
            s.create()
        dst_exp = s.experiment(e['label'])
        if dst_exp.exists():
            log.error('Experiment `{}` already exists. '
                      'Aborting.'.format(dst_exp._urn))
            sys.exit(1)
        src_exp = c1.select.experiment(e['ID'])

        tmp_dir = tempfile.mkdtemp()
        mirror_session(src_exp, dst_exp, tmp_dir, scans, res)
        rmtree(tmp_dir)

    c1.close_jsession()
    c2.close_jsession()


def create_parser():
    import argparse
    from argparse import RawTextHelpFormatter

    desc = 'Creates a selection of data (replicated in a new project) '\
           'from a set of existing imaging sessions.'
    arg_parser = argparse.ArgumentParser(description=desc,
                                         formatter_class=RawTextHelpFormatter)
    arg_parser.add_argument(
        '-c', '--source_config', dest='source_config', required=True,
        help='source XNAT configuration file')
    arg_parser.add_argument(
        '-d', '--dest_config', dest='dest_config', required=False,
        help='destination XNAT configuration file  (optional)')
    arg_parser.add_argument(
        '--list', dest='selection_list', required=True,
        help='CSV file with list of experiments to be replicated')
    arg_parser.add_argument(
        '--label', dest='label', required=True,
        help='label identifying the data selection')
    arg_parser.add_argument(
        '--reuse', dest='reuse_project', action='store_true', default=False,
        help='reuse an existing project (optional)', required=False)
    arg_parser.add_argument(
        '--scans', dest='scans', required=False,
        help='scan types included in the data selection (optional)')
    arg_parser.add_argument(
        '--resources', dest='resources', required=False,
        help='resources included in the data selection (optional)')
    arg_parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true', default=False,
        help='display verbosal information (optional)', required=False)

    return arg_parser


if __name__ == "__main__":
    parser = create_parser()
    arguments = parser.parse_args()

    if arguments.verbose:
        log.basicConfig(level=log.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s:%(module)s:%(levelname)s:%(message)s')

    main(arguments)
    sys.exit(0)
