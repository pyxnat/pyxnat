import os

def find_files(src):
    names = os.listdir(src)

    errors = []
    files = []

    for name in names:
        srcname = os.path.join(src, name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                files.extend(find_files(linkto))
                # os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                files.extend(find_files(srcname))
            else:
                files.append(srcname)
        except (IOError, os.error), why:
            errors.append((srcname, str(why)))

    return files
