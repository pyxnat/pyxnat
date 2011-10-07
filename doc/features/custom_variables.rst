Schemaless Data
---------------

XNAT uses an XML schema to declare datatypes and variables. Howevr it offers
several mechanisms to store data that don't fit in the schemas. The tradeoff
is in general that those data cannot be queried using the search engine.

..
   Custom Variables
   ~~~~~~~~~~~~~~~~

   Variables have to be declared at the project level and then set at any
   StudyProtocol level.


   .. warning:: At the moment this system suffers several limitations:

      - the "first" time, this functionality has to be enabled through the
	web interface by clicking at the "custom variables" button under a 
	project and adding a custom variable.
      - a custom variable cannot be deleted

Parameters
~~~~~~~~~~

Key/value mechanism accessible at the assessor and reconstruction levels.

.. code-block:: python

    >>> assessor.set_param('one', '1')
    >>> assessor.set_param('two', '2')
    >>> assessor.params()
    ['one', 'two']
    >>> assessor.get_param('two')
    '2'

.. warning:: Currently a parameter cannot be deleted.
