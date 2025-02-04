# Since pyxnat v1.2.1.0.post3, we introduced a mechanism to tune these objects
# and allow adding custom functions for specific types of resources.
#
# For instance, one could now directly write:
#
# resource = experiment.resource('FREESURFER6')
# aparc = resource.aparc()
# aseg = resource.aseg()
# and thus get access to FreeSurfer measurements.
#
# Another example, with the ASHS pipeline for hippocampal subfield segmentation:
#
# resource = experiment.resource('ASHS')
# volumes = resource.volumes()
#
# Again, this would only work provided that corresponding resources respect a
# certain naming and structure on XNAT. Here in this present example, FreeSurfer
# results are stored in resources called FREESURFER6 and the whole FreeSurfer
# folder (named after the subject) is stored in the resource. Having access
# to such additional functions would be conditioned by the existence of these
# resources with proper matching structure.
#
# Nevertheless, this mechanism has been implemented so as to get easily adapted
# to local configurations, by editing/adding this very same folder.
#
# Adding a custom function can be done simply as follows.
#
# In this same folder (pyxnat/core/derivatives/), edit any existing file or add a new
# one (filename does not matter):
#
# Define XNAT_RESOURCE_NAME. This variable names the XNAT resource which needs
# a custom function.
# Write the custom function with self as first parameter (self will be the
# pyxnat Resource object).
# If the resources which the custom function should be added has multiple names
# instead of a single one, their list may be provided under the variable
# XNAT_RESOURCE_NAMES.
#
# An example is provided in pyxnat/core/derivatives/ashs.py
# 
