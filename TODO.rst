
* Add some in-code comments on the inner workings of the module

* Support current reserved keywords as resource identifiers

* Improve get file

* Add support for subfolders in files

* Add/update documentation for:
  - search_templates
  - search.saved(_templates) methods
  - provenance
  - nipype and cff integration

* Add/update tests for:
  - provenance
  - templates

* replace the entry point decorator because it hides the functions 
  documentation

* replace Klass = globals()[uri_nextlast(uri).title().rsplit('s', 1)[0]] with something like
  Klass = globals().get(uri_nextlast(uri).title().rsplit('s', 1)[0], Interface)
