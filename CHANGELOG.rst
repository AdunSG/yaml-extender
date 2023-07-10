Changelog
=========

Version 0.0.8, 2023-07-10
-----------------------

- Bugfix: Including files, which represent a list value is now possible.
            + Added additional tests for that

Version 0.0.7, 2023-06-12
-----------------------

- Changed: occurences of list refs in string will now resolve as whitespace separated string.
- Changed: resolving lists in lists will now extend the current list.

- Bugfix: Include Resolver will now resolve subsequent values in dicts.

Version 0.0.6, 2023-05-11
-----------------------

- Added option to enable / disable sorting of yaml keys.

Version 0.0.6, 2023-05-11
-----------------------

- Added option to enable / disable sorting of yaml keys.

Version 0.0.5, 2023-03-02
-----------------------

- Fixed issues with passing include directories over CLI.

Version 0.0.4, 2023-02-28
-----------------------

- Fixed import error due to IDE autocompletion

Version 0.0.3, 2023-02-27
-----------------------

- Added Option to provide additional include directories over CLI.
- Added Option to provide additional include directories to IncludeResolver.
- Added possibility to merge values in nested dictionaries on include.
