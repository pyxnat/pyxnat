Xpath Store
-----------

This store is another use of the local cache directory. It basically
enables users to perform xpath queries on subjects XML documents. It
also provides a few utility functions to help figure out what information
is in the documents.

An xpath example to retrieve the IDs from all the subjects in cache:

.. code-block:: python

   >>> central.xpath('//xnat:Subject/attribute::ID')

Download the XML documents from a project or from a subject list:

.. code-block:: python

   >>> central.xpath.checkout(project='my_project')
   >>> central.xpath.checkout(subjects=['CENTRAL_00001', 'CENTRAL_00005'])

Update the subjects XML documents if any data related to them has changed
on the server since the last update:

.. code-block:: python

   >>> central.xpath.update()

.. warning: currently the creation date of the cached files are checked
   against the time of the server. If the server is not in the same
   time zone you can encounter some issues. This will be fixed.

Helper methods to get the subject IDs, the subject attributes, the
elements attached to subject and their attributes or text elements:

.. code-block:: python

   >>> central.xpath.subjects()
   >>> central.xpath.keys()
   >>> central.xpath.values('key')
   >>> central.xpath.attrs()
   >>> central.xpath.elements()
   >>> central.xpath.element_keys('element_name')
   >>> central.xpath.element_values('element_name')
   >>> central.xpath.element_attrs('element_name')
   >>> central.xpath.element_text('element_name')
