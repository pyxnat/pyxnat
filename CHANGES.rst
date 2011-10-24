Latest changes
===============

Release 0.9.0
-------------

    * New features:
        - Global listing functions:
            - interface.array.experiments()
	    - interface.array.search_experiments()
	    - interface.array.scans()
	       
        - Support for XNAT configuration file format
        - Batch function for downloading all files related to a scan or an assessor
        - Create element with an XML document
        - New xpath function for EObjects
        - xpath store facility to query cached subject XMLs with xpath

    * Improvements:
        - Catching authentication errors
        - Toggle option for cache warnings
        - Description for search templates is displayed
      
    * Bug fixes:
        - Config file

Release 0.8.0
-------------

    * Compatible with XNAT 1.5

    * New features:
        - provenance annotation on assessors and recontructions
	- search templates
	- callback system to monitor data streams to and from the server

    * Improvements:
        - support for proxies in the Interface object
	- a description can be added when a search is saved on the server
	- python strings can be uploaded and saved just like files

    * Bug fixes including:
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
