Latest changes
===============

Release 0.7.0
----------------

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
