XNAT_RESOURCE_NAME = 'DONSURF'


def aparc(self):
    """Returns cortical features as estimated by `DONSURF`."""

    from .freesurfer import aparc as fs_aparc
    return fs_aparc(self)
