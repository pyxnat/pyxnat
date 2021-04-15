XNAT_RESOURCE_NAME = 'DONSURF'


def aparc(self):
    """Returns cortical features as estimated by `DONSURF`."""

    from .freesurfer import aparc
    return aparc(self)
