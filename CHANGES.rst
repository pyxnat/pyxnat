:orphan:

Latest changes
===============

Release 1.3.0.0
---------------

     - Docker-based tests are temporarily removed from Travis
     - Tests are now included with the PyPI package     


Release 1.2.0.0
---------------

      * New Features

         - CI tests can be skipped if no network connectivity or no Docker-based XNAT available
         - bin/sessionmirror.py: migrate an experiment between two XNAT instances

      * Improvements

         - More tests
         - Refreshing documentation

      * Bug fixes

         - XNAT REST API compatibility (`Interfaces.version()`, `Schemas`, etc)
         - Removed deprecated references to cache support
         - Python 3 fixes


Release 1.1.0.2
---------------

      * Improvements

         - Refreshing documentation

      * Bug fixes

         - If verify not defined, don't store it
         - Closing requests session on disconnection

Release 1.1.0.0
---------------

    * New Features

      - Python 3 compatibility

    * Improvements

       - Get aliases from a project
       - CI tests may now (partially) run within a Docker container
       - `ArrayData` class makes no more assumption on data type and use broader/generic types (avoids missing results from other types)
       - Specific methods added for MRSessions and MRScans
       - Added certification verification to configuration file
       - Added test coverage

    * Bug fixes

       - CI tests run again (partially)
       - Fixed vulnerability (upgraded `requests` package version)
       - Replaced '\n' newline chars by an OS-agnostic alternative

Release 1.0.1.0
---------------

    * New Features

    * Improvements
        - Pass keyword arguments on some put/create methods, to allow passing event_reason.

    * Bug fixes
        - Minor docs inconsistencies that generated sphinx warnings
        - Clean up deprecated references in sphinx autogenerate extension
        - Remove deprecated sphinx plugin pngmath in favor of imgmath

Release 1.0.0.0
---------------

    * New Features
        - Convenience methods on interface: get, put, post, delete, head
        - Verify option on interface for ssl-cert-verification

    * Improvements
        - More useful error messages when things go wrong
        - streaming file upload
        - streaming file download
        - Use the requests library instead of httplib2 for REST calls

    * Bug fixes
        - Removed custom httplib2 caching.

Release 0.9.5.2
---------------

    * New Features

    * Improvements

    * Bug fixes
        - Ticket #50 404 error causes connection to be broken until end of object life.
        - Tiekct #52 fix zip file downloading.

Release 0.9.5
-------------

    * New Features
        - Add __getitem__ to CObject for slice operations.


    * Improvements
        - Add toggle for overwriting files on the Resources object (put, put_dir, put_zip)
        - Add toggle for not extracting the zip file on the Resources object (put, put_dir, put_zip)

    * Bug fixes
        - fix proxy support
        - mset attributes fixed
        - fixed url separator issue on windows.


Release 0.9.4
-------------

    * New Features
        - add proxy support to interface.

    * Improvements

    * Bug fixes
        - python <2.7 compatibility.
        - project.parent() does not throw error.
        - removed simplejson requirement
        - md5 cache key



Release 0.9.0
-------------

    * New features
        - Global listing functions:
            - interface.array.experiments()
	    - interface.array.search_experiments()
	    - interface.array.scans()

        - Support for XNAT configuration file format
        - Batch function for downloading all files related to a scan or an assessor
        - Create element with an XML document
        - New xpath function for EObjects
        - xpath store facility to query cached subject XMLs with xpath

    * Improvements
        - Catching authentication errors
        - Toggle option for cache warnings
        - Description for search templates is displayed

    * Bug fixes
        - Config file

Release 0.8.0
-------------

    * Compatible with XNAT 1.5

    * New features
        - provenance annotation on assessors and recontructions
	- search templates
	- callback system to monitor data streams to and from the server

    * Improvements
        - support for proxies in the Interface object
	- a description can be added when a search is saved on the server
	- python strings can be uploaded and saved just like files

    * Bug fixes including
        - improved unicode support for uploaded files
	- solved cache issue on Windows
	- a major bug in the Collection.where method

Release 0.7.0
-------------

    * Errors following the PEP-249

    * Some operations follow the PEP-249 - e.g. `fetchall` replaces `get`

    * New inspection functions:
          - experiement_types
	  - assessor_types
	  - scan_types
	  - reconstruction_types
	  - project_values
	  - subject_values
	  - experiment_values
	  - assessor_values
	  - scan_values
	  - reconstruction_values

    * Inspect method `fieldvalues` changed to `field_values`

    * `Interface` Object now supports config files.

    * Bug fix regarding the file names in the cache. It means that cached data
      from older versions has to be re-downloaded.

    * The disk check for available space is performed against a timer instead
      of always.

    * The default `get` function to download file now supports custom paths.

    * Bug fix for HTTP sessions management.

    * New `last_modified` method for project to get subjects last modified
      date.

    * Resource elements are now fully configurable at creation.

    * Added support for XNAT pipelines.

    * Added push and pull zip files at the resource level.

    * Added simple schema parsing capabilities.

    * Add a global management interface to gather different managers.

    * Interface now follows redirections on the server url.
