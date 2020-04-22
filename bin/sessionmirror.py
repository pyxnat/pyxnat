#!/usr/bin/env python
'''
The MIT License (MIT)

Copyright (c) 2014 VUIIS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
Adapted from xnatmirror (https://github.com/VUIIS/dax/blob/master/bin/Xnat_tools/Xnatmirror)
'''

def cmp(a, b):
    return (a > b) - (a < b)

from builtins import zip
from builtins import str

import os
import os.path as op
import sys

from xml.etree import cElementTree as ET
import pyxnat

PROJ_ATTRS = [
    'xnat:projectData/name',
    'xnat:projectData/description',
    'xnat:projectData/keywords',
]

SUBJ_ATTRS = [
    'xnat:subjectData/group',
    'xnat:subjectData/src',
    'xnat:subjectData/investigator/firstname',
    'xnat:subjectData/investigator/lastname',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/dob',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/yob',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/age',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/gender',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/handedness',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/ses',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/education',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/\
educationDesc',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/race',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/ethnicity',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/weight',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/height',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/\
gestational_age',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/\
post_menstrual_age',
    'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/\
birth_weight'
]

MR_EXP_ATTRS = [
    'xnat:experimentData/date',
    'xnat:experimentData/visit_id',
    'xnat:experimentData/time',
    'xnat:experimentData/note',
    'xnat:experimentData/investigator/firstname',
    'xnat:experimentData/investigator/lastname',
    'xnat:imageSessionData/scanner/manufacturer',
    'xnat:imageSessionData/scanner/model',
    'xnat:imageSessionData/operator',
    'xnat:imageSessionData/dcmAccessionNumber',
    'xnat:imageSessionData/dcmPatientId',
    'xnat:imageSessionData/dcmPatientName',
    'xnat:imageSessionData/session_type',
    'xnat:imageSessionData/modality',
    'xnat:imageSessionData/UID',
    'xnat:mrSessionData/coil',
    'xnat:mrSessionData/fieldStrength',
    'xnat:mrSessionData/marker',
    'xnat:mrSessionData/stabilization'
]

OTHER_DICOM_SCAN_ATTRS = [
    'xnat:imageScanData/type',
    'xnat:imageScanData/UID',
    'xnat:imageScanData/note',
    'xnat:imageScanData/quality',
    'xnat:imageScanData/condition',
    'xnat:imageScanData/series_description',
    'xnat:imageScanData/documentation',
    'xnat:imageScanData/frames',
    'xnat:imageScanData/startTime',
    'xnat:imageScanData/scanner/manufacturer',
    'xnat:imageScanData/scanner/model'
]

MR_SCAN_ATTRS = [
    'xnat:imageScanData/type',
    'xnat:imageScanData/UID',
    'xnat:imageScanData/note',
    'xnat:imageScanData/quality',
    'xnat:imageScanData/condition',
    'xnat:imageScanData/series_description',
    'xnat:imageScanData/documentation',
    'xnat:imageScanData/frames',
    'xnat:imageScanData/startTime',
    'xnat:imageScanData/scanner/manufacturer',
    'xnat:imageScanData/scanner/model',
    'xnat:mrScanData/parameters/flip',
    'xnat:mrScanData/parameters/orientation',
    'xnat:mrScanData/parameters/tr',
    'xnat:mrScanData/parameters/ti',
    'xnat:mrScanData/parameters/te',
    'xnat:mrScanData/parameters/sequence',
    'xnat:mrScanData/parameters/imageType',
    'xnat:mrScanData/parameters/scanSequence',
    'xnat:mrScanData/parameters/seqVariant',
    'xnat:mrScanData/parameters/scanOptions',
    'xnat:mrScanData/parameters/acqType',
    'xnat:mrScanData/parameters/pixelBandwidth',
    'xnat:mrScanData/parameters/voxelRes/x',
    'xnat:mrScanData/parameters/voxelRes/y',
    'xnat:mrScanData/parameters/voxelRes/z',
    'xnat:mrScanData/parameters/fov/x',
    'xnat:mrScanData/parameters/fov/y',
    'xnat:mrScanData/parameters/matrix/x',
    'xnat:mrScanData/parameters/matrix/y',
    'xnat:mrScanData/parameters/partitions',
    'xnat:mrScanData/fieldStrength',
    'xnat:mrScanData/marker',
    'xnat:mrScanData/stabilization',
    'xnat:mrScanData/coil'
]

SC_SCAN_ATTRS = [
    'xnat:imageScanData/type',
    'xnat:imageScanData/UID',
    'xnat:imageScanData/note',
    'xnat:imageScanData/quality',
    'xnat:imageScanData/condition',
    'xnat:imageScanData/series_description',
    'xnat:imageScanData/documentation',
    'xnat:imageScanData/frames',
    'xnat:imageScanData/scanner/manufacturer',
    'xnat:imageScanData/scanner/model'
]

PET_EXP_ATTRS = [
    'xnat:experimentData/date',
    'xnat:experimentData/visit_id',
    'xnat:experimentData/time',
    'xnat:experimentData/note',
    'xnat:experimentData/investigator/firstname',
    'xnat:experimentData/investigator/lastname',
    'xnat:imageSessionData/scanner/manufacturer',
    'xnat:imageSessionData/scanner/model',
    'xnat:imageSessionData/operator',
    'xnat:imageSessionData/dcmAccessionNumber',
    'xnat:imageSessionData/dcmPatientId',
    'xnat:imageSessionData/dcmPatientName',
    'xnat:imageSessionData/session_type',
    'xnat:imageSessionData/modality',
    'xnat:imageSessionData/UID',
    'xnat:petSessionData/studyType',
    'xnat:petSessionData/patientID',
    'xnat:petSessionData/patientName',
    'xnat:petSessionData/stabilization',
    'xnat:petSessionData/start_time/scan',
    'xnat:petSessionData/start_time/injection',
    'xnat:petSessionData/tracer/name',
    'xnat:petSessionData/tracer/startTime',
    'xnat:petSessionData/tracer/dose',
    'xnat:petSessionData/tracer/specificActivity',
    'xnat:petSessionData/tracer/totalMass',
    'xnat:petSessionData/tracer/intermediate',
    'xnat:petSessionData/tracer/isotope',
    'xnat:petSessionData/tracer/isotope/half-life',
    'xnat:petSessionData/tracer/transmissions',
    'xnat:petSessionData/tracer/transmissions/startTime'
]

CT_EXP_ATTRS = [
    'xnat:experimentData/date',
    'xnat:experimentData/visit_id',
    'xnat:experimentData/time',
    'xnat:experimentData/note',
    'xnat:experimentData/investigator/firstname',
    'xnat:experimentData/investigator/lastname',
    'xnat:imageSessionData/scanner/manufacturer',
    'xnat:imageSessionData/scanner/model',
    'xnat:imageSessionData/operator',
    'xnat:imageSessionData/dcmAccessionNumber',
    'xnat:imageSessionData/dcmPatientId',
    'xnat:imageSessionData/dcmPatientName',
    'xnat:imageSessionData/session_type',
    'xnat:imageSessionData/modality',
    'xnat:imageSessionData/UID'
]

PET_SCAN_ATTRS = [
    'xnat:imageScanData/type',
    'xnat:imageScanData/UID',
    'xnat:imageScanData/note',
    'xnat:imageScanData/quality',
    'xnat:imageScanData/condition',
    'xnat:imageScanData/series_description',
    'xnat:imageScanData/documentation',
    'xnat:imageScanData/frames',
    'xnat:imageScanData/scanner/manufacturer',
    'xnat:imageScanData/scanner/model',
    'xnat:imageScanData/startTime',
    'xnat:petScanData/parameters/orientation',
    'xnat:petScanData/parameters/originalFileName',
    'xnat:petScanData/parameters/systemType',
    'xnat:petScanData/parameters/fileType',
    'xnat:petScanData/parameters/transaxialFOV',
    'xnat:petScanData/parameters/acqType',
    'xnat:petScanData/parameters/facility',
    'xnat:petScanData/parameters/numPlanes',
    'xnat:petScanData/parameters/frames/numFrames',
    'xnat:petScanData/parameters/numGates',
    'xnat:petScanData/parameters/planeSeparation',
    'xnat:petScanData/parameters/binSize',
    'xnat:petScanData/parameters/dataType'
]

CT_SCAN_ATTRS = [
    'xnat:imageScanData/type',
    'xnat:imageScanData/UID',
    'xnat:imageScanData/note',
    'xnat:imageScanData/quality',
    'xnat:imageScanData/condition',
    'xnat:imageScanData/series_description',
    'xnat:imageScanData/documentation',
    'xnat:imageScanData/frames',
    'xnat:imageScanData/scanner/manufacturer',
    'xnat:imageScanData/scanner/model'
]

PROC_ATTRS = [
    'proc:genProcData/validation/status',
    'proc:genProcData/procstatus',
    'proc:genProcData/proctype',
    'proc:genProcData/procversion',
    'proc:genProcData/walltimeused',
    'proc:genProcData/memused'
]


def copy_attrs(src_obj, dest_obj, attr_list):
    """ Copies list of attributes form source to destination"""
    src_attrs = src_obj.attrs.mget(attr_list)
    src_list = dict(list(zip(attr_list, src_attrs)))

    # NOTE: For some reason need to set te again b/c a bug somewhere sets te
    # to sequence name
    te_key = 'xnat:mrScanData/parameters/te'
    if te_key in src_list:
        src_list[te_key] = src_obj.attrs.get(te_key)

    dest_obj.attrs.mset(src_list)
    return 0


def copy_attributes(src_obj, dest_obj):
    '''Copy attributes from src to dest'''
    src_type = src_obj.datatype()

    if src_type == 'xnat:projectData':
        copy_attrs(src_obj, dest_obj, PROJ_ATTRS)
    elif src_type == 'xnat:subjectData':
        copy_attrs(src_obj, dest_obj, SUBJ_ATTRS)
    elif src_type == 'xnat:mrSessionData':
        copy_attrs(src_obj, dest_obj, MR_EXP_ATTRS)
    elif src_type == 'xnat:petSessionData':
        copy_attrs(src_obj, dest_obj, PET_EXP_ATTRS)
    elif src_type == 'xnat:ctSessionData':
        copy_attrs(src_obj, dest_obj, CT_EXP_ATTRS)
    elif src_type == 'xnat:mrScanData':
        copy_attrs(src_obj, dest_obj, MR_SCAN_ATTRS)
    elif src_type == 'xnat:petScanData':
        copy_attrs(src_obj, dest_obj, PET_SCAN_ATTRS)
    elif src_type == 'xnat:ctScanData':
        copy_attrs(src_obj, dest_obj, CT_SCAN_ATTRS)
    elif src_type == 'xnat:scScanData':
        copy_attrs(src_obj, dest_obj, SC_SCAN_ATTRS)
    elif src_type == 'proc:genProcData':
        copy_attrs(src_obj, dest_obj, PROC_ATTRS)
    elif src_type == 'xnat:otherDicomScanData':
        copy_attrs(src_obj, dest_obj, OTHER_DICOM_SCAN_ATTRS)
    else:
        print('ERROR:cannot copy attributes, unsupported datatype:' + src_type)


def subj_compare(item1, item2):
    '''Compare sort of items'''
    return cmp(item1.label(), item2.label())


def copy_file(src_f, dest_r, cache_d):
    '''
    Copy file from XNAT file source to XNAT resource destination,
    using local cache in between'''
    f_label = src_f.label()
    loc_f = cache_d + '/' + f_label

    # Make subdirectories
    loc_d = op.dirname(loc_f)
    if not op.exists(loc_d):
        os.makedirs(loc_d)

    try:
        # Download file
        if op.exists(loc_f) is False:
            src_f.get(loc_f)

        # Get File Attributes
        f_in_attrs = src_f.attributes()
        f_content = f_in_attrs.get('file_content')
        f_format = f_in_attrs.get('file_format')
        f_tags = f_in_attrs.get('file_tags')

        # Upload File
        if f_format and f_content and not f_tags:         # format & content
            dest_r.file(f_label).put(loc_f, f_format, f_content)
        elif f_format and not f_content and not f_tags:   # format only
            dest_r.file(f_label).put(loc_f, f_format)
        elif f_format and f_content and f_tags:   # format, content, & tags
            dest_r.file(f_label).put(loc_f, f_format, f_content)
        else:                                             # none
            dest_r.file(f_label).put(loc_f)

        # Delete local copy
        os.remove(loc_f)
    except Exception:
        print("ERROR:failed to copy file:%s, error=%s"
              % (f_label, sys.exc_info()[0]))


def copy_res_zip(src_r, dest_r, cache_d):
    '''
    Copy a resource from XNAT source to XNAT destination using local cache
    in between
    '''
    try:
        # Download zip of resource
        print('INFO:Downloading resource as zip...')
        cache_z = src_r.get(cache_d, extract=False)

        # Upload zip of resource
        print('INFO:Uploading resource as zip...')
        dest_r.put_zip(cache_z, extract=True)

        # Delete cached zip
        os.remove(cache_z)

    except IndexError:
        print('ERROR:failed to copy:%s:%s' % (cache_z, sys.exc_info()[0]))
        raise


def is_empty_resource(_res):
    '''Check if resource contains any files'''
    f_count = 0
    for f_in in _res.files().fetchall('obj'):
        f_count += 1
        break

    return f_count == 0

# copy_project and copy_subject are untested

# def copy_project(src_proj, dst_proj, proj_cache_dir):
#     '''Copy XNAT project from source to destination'''
#
#     if not dst_proj.exists():
#         try:
#             dst_proj.create()
#         except Exception as e:
#             msg = 'ERROR: can not create project on destination '\
#                 'xnat. Check your user rights. %s' % e
#             raise Exception(msg)
#         copy_attributes(src_proj, dst_proj)
#     print('INFO:loading and sorting subject list...')
#
#     proj_label = src_proj.label()
#     subj_list = src_xnat.get_subjects(proj_label)
#     subj_list = [x for x in subj_list if x['label'] not in SUBJECTS_MIRRORED]
#     subj_i = 0
#     for subj in subj_list:
#         subj_i += 1
#         subject_label = subj['label']
#
#         print("INFO:Processing subject %s (%d)..." % (subject_label, subj_i))
#         src_subj = src_proj.subject(subject_label)
#         dst_subj = dst_proj.subject(subject_label)
#         subj_cache_dir = op.join(proj_cache_dir, subject_label)
#         copy_subject(src_subj, dst_subj, subj_cache_dir)


# def copy_subject(src_subj, dst_subj, subj_cache_dir):
#     '''Copy subject from XNAT src to XNAT dst'''
#
#     if not dst_subj.exists():
#         print('INFO:uploading subject attributes as xml')
#
#         # Create dirs
#         if not op.exists(subj_cache_dir):
#             os.makedirs(subj_cache_dir)
#
#         # Write xml to file
#         subj_xml = src_subj.get()
#         xml_path = op.join(subj_cache_dir, 'subj.xml')
#         write_xml(subj_xml, xml_path)
#         dst_subj.create(xml=xml_path, allowDataDeletion=False)
#
#     # Process each experiment of subject
#     for src_sess in src_subj.experiments().fetchall('obj'):
#         sess_label = src_sess.label()
#         sess_type = src_sess.datatype()
#         if sess_type != 'xnat:mrSessionData' and \
#            sess_type != 'xnat:petSessionData' and \
#            sess_type != 'xnat:ctSessionData':
#             print('WARN:Skipping, session is not MR, CT, or PET Session')
#             continue
#
#         print("INFO:Processing session:%s..." % (sess_label))
#
#         dst_sess = dst_subj.experiment(sess_label)
#         sess_cache_dir = op.join(subj_cache_dir, sess_label)
#         copy_session(src_sess, dst_sess, sess_cache_dir)


def copy_session(src_sess, dst_sess, sess_cache_dir):
    '''Copy XNAT session from source to destination'''

    print(dst_sess.exists())
    print(dst_sess._uri)
    print('INFO:uploading session attributes as xml')
    # Write xml to file
    if not op.exists(sess_cache_dir):
        os.makedirs(sess_cache_dir)
    sess_xml = src_sess.get()
    xml_path = op.join(sess_cache_dir, 'sess.xml')
    write_xml(sess_xml, xml_path)
    print(xml_path)

    sess_type = src_sess.datatype()
    dst_sess.create(experiments=sess_type)
    copy_attributes(src_sess, dst_sess)

    # Process each scan of session
    for src_scan in src_sess.scans().fetchall('obj'):
        scan_label = src_scan.label()

        print('INFO:Processing scan:%s...' % scan_label)
        dst_scan = dst_sess.scan(scan_label)
        scan_cache_dir = op.join(sess_cache_dir, scan_label)
        copy_scan(src_scan, dst_scan, scan_cache_dir)

    # Process each assessor of session
    for src_assr in src_sess.assessors():
        assr_label = src_assr.label()
        print('INFO:Processing assessor:%s:...' % assr_label)
        dst_assr = dst_sess.assessor(assr_label)
        assr_cache_dir = op.join(sess_cache_dir, assr_label)
        copy_assr(src_assr, dst_assr, assr_cache_dir)

    for src_res in src_sess.resources().fetchall('obj'):
        res_label = src_res.label()

        print('INFO:Processing resource:%s...' % (res_label))

        dst_res = dst_sess.resource(res_label)

        res_cache_dir = op.join(scan_cache_dir, res_label)

        copy_res(src_res, dst_res, res_cache_dir, use_zip=True)

def copy_scan(src_scan, dst_scan, scan_cache_dir):
    '''Copy scan from source XNAT to destination XNAT'''

    scan_type = src_scan.datatype()
    if scan_type == '':
             scan_type = 'xnat:otherDicomScanData'
    dst_scan.create(scans=scan_type)
    copy_attributes(src_scan, dst_scan)

    # Process each resource of scan
    for src_res in src_scan.resources().fetchall('obj'):
        res_label = src_res.label()

        print('INFO:Processing resource:%s...' % (res_label))

        dst_res = dst_scan.resource(res_label)

        res_cache_dir = op.join(scan_cache_dir, res_label)
        if res_label == 'SNAPSHOTS':
            copy_res(src_res, dst_res, res_cache_dir)
        else:
            copy_res(src_res, dst_res, res_cache_dir, use_zip=True)


def copy_res(src_res, dst_res, res_cache_dir, use_zip=False):
    '''Copy resource from source XNAT to destination XNAT'''
    # Create cache dir
    if not op.exists(res_cache_dir):
        os.makedirs(res_cache_dir)

    # Prepare resource and check for empty
    is_empty = False
    print(dst_res._uri)
    if not dst_res.exists():
        dst_res.create()
        is_empty = True
    elif is_empty_resource(dst_res):
        is_empty = True

    # Check for empty source
    if is_empty_resource(src_res):
        print('WARN:empty resource, nothing to copy')
        return

    if is_empty:
        if use_zip:
            # Try to copy as zip
            try:
                print('INFO:Copying resource as zip: %s...' % src_res.label())
                copy_res_zip(src_res, dst_res, res_cache_dir)
                return
            except Exception:
                try:
                    print('INFO: second attempt to copy resource as zip: %s...'
                          % src_res.label())
                    copy_res_zip(src_res, dst_res, res_cache_dir)
                    return
                except Exception:
                    msg = 'ERROR:failed twice to copy resource as zip, will'\
                        'copy individual files'
                    print(msg)

        copy_count = 0
        for f in src_res.files():
            print('INFO:Copying file: %s...' % f.label())
            copy_count += 1
            copy_file(f, dst_res, res_cache_dir)
        print('INFO:Finished copying resource, %d files copied' % copy_count)


def copy_assr(src_assr, dst_assr, assr_cache_dir):
    '''Copy assessor from source XNAT to destination XNAT'''

    # Check type
    assr_type = src_assr.datatype()
    if assr_type != 'proc:genProcData' and assr_type != 'fs:fsData':
        print('WARN:skipping unsupported assessor type: {}'.format(assr_type))
        return

    if not dst_assr.exists():
        print('INFO:uploading assessor attributes as xml')
        # Write xml to file
        if not op.exists(assr_cache_dir):
            os.makedirs(assr_cache_dir)
        assr_xml = src_assr.get()
        xml_path = op.join(assr_cache_dir, 'assr.xml')
        write_xml(assr_xml, xml_path)
        dst_assr.create(xml=xml_path, allowDataDeletion=False)

    # Process each resource of assr
    for src_res in src_assr.out_resources():
        res_label = src_res.label()
        print('INFO:Processing resource:%s...' % res_label)
        dst_res = dst_assr.out_resource(res_label)
        res_cache_dir = op.join(assr_cache_dir, res_label)

        if res_label == 'SNAPSHOTS':
            copy_res(src_res, dst_res, res_cache_dir)
        else:
            copy_res(src_res, dst_res, res_cache_dir, use_zip=True)

def write_xml(xml_str, file_path, clean_tags=True):
    """Writing XML."""
    root = ET.fromstring(xml_str)

    # We only want the tags and attributes relevant to root, no children
    if clean_tags:
        # Remove ID
        if 'ID' in root.attrib:
            del root.attrib['ID']

        # Remove sharing tags
        tag = '{http://nrg.wustl.edu/xnat}sharing'
        for child in root.findall(tag):
            root.remove(child)

        # Remove out
        for child in root.findall('{http://nrg.wustl.edu/xnat}out'):
            root.remove(child)
            break

        # Remove session ID
        tag = '{http://nrg.wustl.edu/xnat}imageSession_ID'
        for child in root.findall(tag):
            root.remove(child)

        # Remove subject ID
        for child in root.findall('{http://nrg.wustl.edu/xnat}subject_ID'):
            root.remove(child)

        # Remove _session ID
        tag = '{http://nrg.wustl.edu/xnat}image_session_ID'
        for child in root.findall(tag):
            root.remove(child)

        # Remove scans
        for child in root.findall('{http://nrg.wustl.edu/xnat}scans'):
            root.remove(child)
            break

        # Remove assessors
        for child in root.findall('{http://nrg.wustl.edu/xnat}assessors'):
            root.remove(child)
            break

        # Remove resources
        for child in root.findall('{http://nrg.wustl.edu/xnat}resources'):
            root.remove(child)
            break

        # Remove experiments
        for child in root.findall('{http://nrg.wustl.edu/xnat}experiments'):
            root.remove(child)
            break

    try:
        # Write to file
        ET.register_namespace('xnat', 'http://nrg.wustl.edu/xnat')
        ET.register_namespace('proc', 'http://nrg.wustl.edu/proc')
        ET.register_namespace('prov', 'http://www.nbirn.net/prov')
        ET.register_namespace('fs', 'http://nrg.wustl.edu/fs')
        ET.ElementTree(root).write(file_path)
    except IOError as error:
        print('ERROR:writing xml file: {}: {}'.format(file_path, str(error)))



def create_parser():
    import argparse
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description='Downloads a given experiment/'\
        'session from an XNAT instance and uploads it to an independent one. '\
        'Only DICOM resources will be imported. \n\n'\
        'More information at: https://wiki.xnat.org/docs16/4-developer-documen'\
        'tation/xnat-rest-api-directory/data-services-import',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--h1', '--source_config', dest='source_config',
        help='Source XNAT configuration file', required=True)
    parser.add_argument('--h2', '--dest_config', dest='dest_config',
        help='Destination XNAT configuration file', required=True)
    parser.add_argument('-e','--experiment_id',
        help='Which resource to download? (Entity name/identifier)', required=True)
    parser.add_argument('-p','--project_id', dest='project_id',
        help='Which project to store the resource in', required=True)

    parser.add_argument('-v','--verbose', dest='verbose', action='store_true',
        default=False, help='Display verbosal information (optional)',
        required=False)

    return parser



def main(args):
    x1 = pyxnat.Interface(config=args.source_config)
    x2 = pyxnat.Interface(config=args.dest_config)

    columns = ['subject_label', 'label']
    e1 = x1.array.experiments(experiment_id=args.experiment_id,
        columns=columns).data[0]
    p = x2.select.project(args.project_id)
    s = p.subject(e1['subject_label'])
    if not s.exists():
       s.create()
    e = s.experiment(e1['label'])
    e.create()

    src_sess = x1.select.project(e1['project']).subject(e1['subject_ID']).experiment(e1['ID'])
    dst_sess = e

    copy_session(src_sess, dst_sess, '/tmp')


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)
