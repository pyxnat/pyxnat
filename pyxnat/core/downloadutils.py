import os.path as op
import zipfile
import sys

from .schema import class_name
from . import uriutil

DEBUG = False


def unzip(fzip,
          dest_dir,
          check={'run': lambda z, d: True, 'desc': ""}):
    """
    Extracts the given zip file to the given directory, but only if all members
    of the archive pass the given check.

        Parameters
        ----------
        src: fzip
            zipfile
        dest_dir: string
            directory into which to extract the archive
        check: dict
            An dictionary that has the keys:
                 'run' : A function that takes a filename and parent directory
                     and returns Bool. By default this function always returns
                     True.
                 'dest' : A string description of this test. By default this
                     is empty.

        Returns a tuple of type (bool,[string]) where if the extraction ran
        successfully the first is true and the second is a list of files that
        were extracted, and if not the first is false and the second is the
        name of the failing member.
    """
    for member in fzip.namelist():
        if not check['run'](member, dest_dir):
            return (False, member)

    fzip.extractall(path=dest_dir)
    return (True, map(lambda f: op.join(dest_dir, f), fzip.namelist()))


def download(dest_dir, instance=None, type="ALL", name=None, extract=False,
             safe=False, removeZip=False):
    """
    Download all the files at this level that match the given constraint as a
    zip archive. Should not be called directly but from a instance of class
    that supports bulk downloading eg. "Scans"

        Parameters
        ----------
        instance : 'object
             The instance that contains local values needed by this function
             eg. instance._cbase stores the URI.
        dest_dir : string
             directory into which to place the downloaded archive.
        type: string
             a comma separated list of file types, eg. "T1,T2". Default is
             "ALL".
        name: string
             the name of the zip archive. Defaults to None. See below for the
             default naming scheme.
        extract: bool
             If True, the files are left extracted in the parent directory.
             Default is False.
        safe: bool
             If true, run safety checks on the files before extracting,
             eg. check that the file doesn't exist in the parent directory
             before overwriting it. Default is False.

        Default Zip Name
        ----------------
        Given the project "p", subject "s" and experiment "e", and that the
        "Scans" (as opposed to "Assessors" or "Reconstructions") are being
        downloaded, and the scan types are constrained to "T1,T2", the name of
        the zip file defaults to:
          "p_s_e_scans_T1_T2.zip"

        Exceptions
        ----------
        A generic Exception will be raised if any of the following happen:
         - This function is called directly and not from an instance of a
            class that supports bulk downloading eg."Scans"
         - The destination directory is unspecified
        A LookupError is raised if there are no resources to download
        A ValueError is raised if any of the following happen:
         - The project, subject and experiment names could not be extracted
            from the URI
         - The type constraint "ALL" is used with other constraints.
            eg. "ALL,T1,T2"
         - The URI associated with this class contains wildcards
            eg. /projects/proj/subjects/*/experiments/scans
        An EnvironmentError is raised if any of the following happen:
         - If "safe" is true, and (a) a zip file with the same name exists in
            given destination directory or
           (b) extracting the archive overrides an existing file. In the second
            case the downloaded archive
           is left in the parent directory.

        Return
        ------
        A path to the zip archive if "extract" is False, and a list of
        extracted files if True.
    """

    if instance is None:
        raise Exception('This function should be called directly but from an'
                        'instance of a class that supports bulk downloading, '
                        'eg. "Scans"')
    if dest_dir is None:
        raise Exception('Destination directory is unspecified')

    # the URI must be fully qualified with a project,subject and experiment
    if '%2A' in instance._cbase:
        raise ValueError('URI contains wildcards :' + instance._cbase)

    # Check that there are resources at this level
    available = instance.get()
    if len(available) == 0:
        raise LookupError(
            'There are no %s to download' % class_name(instance).lower())

    pse = uriutil.extract_uri(instance._cbase)
    if pse is None:
        raise ValueError("Could not extract project, subject and experiment "
                         "from the uri: " + instance._cbase)

    # Extract the desired scan types. Clean up whitespace and remove dupes
    types = {}
    for t in type.split(','):
        cleaned = t.strip()
        if cleaned != "":
            types[cleaned] = cleaned

    # Make sure the user hasn't asked us to download ALL the scans and then
    # asked for them to be constrained to a type.
    if len(types) > 1 and 'ALL' in types:
        raise ValueError('The \"ALL\" scan type constraint cannot be used with'
                         ' any other constraint')

    (p, s, e) = pse

    # Make the name of the zip file
    default_zip_name = lambda: '%s_%s_%s_%s_%s' % (
        p, s, e, class_name(instance).lower(), '_'.join(types.values()))

    zip_name = name if name is not None else default_zip_name()
    zip_location = op.join(dest_dir, zip_name + '.zip')

    if safe:
        if op.exists(zip_location):
            raise EnvironmentError("Unable to download to " + zip_location +
                                   " because this file already exists.")

    # Download from the server
    with open(zip_location, 'wb') as f:
        response = instance._intf.get(uriutil.join_uri(
            instance._cbase, ','.join(types.values())) + '/files?format=zip',
            stream=True)
        try:
            count = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    count += 1
                    if count % 10 == 0:
                        # flush the buffer every once in a while.
                        f.flush()
            f.flush()  # and one last flush.
        except Exception as e:
            sys.stderr.write(e)
        finally:
            response.close()

    if DEBUG:
        print(zip_location)

    ##

    # Extract the archive
    fzip = zipfile.ZipFile(zip_location, 'r')
    if extract:
        check = {'run': lambda f, d: not op.exists(op.join(dest_dir, f)),
                 'desc': 'File does not exist in the parent directory'}
        safeUnzip = lambda: unzip(fzip, dest_dir, check) \
            if safe else lambda: unzip(fzip, dest_dir)
        (unzipped, paths) = safeUnzip()()
        if not unzipped:
            fzip.close()
            msg = "Unable to extract " + zip_location + " because file " +\
                paths + " failed the following test: " + check['desc']
            raise EnvironmentError(msg)
        else:
            if removeZip:
                fzip.close()
                import os
                os.remove(zip_location)
            return paths
    else:
        fzip.close()
        return zip_location
