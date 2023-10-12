Changelog
=========

Version 0.3.1, 2023-10-12
-----------------------

- Bugfix: Using references as default values works now as expected. Issue#6
- Bugfix: For loops should now resolve correctly if given as part of a dictionary. Issue#2
- Bugfix: For loops will not reverse the order of the elements. Issue#4
- Bugfix: Referencing lists in other lists will now extend the lists correctly. Issue#5

Tests:
- Added: Added tests for above fixes
- Bugfix: Fixed problem with system test being cwd dependent.

Version 0.3.0, 2023-08-31
-----------------------

- MAJOR Changed: List indices are now accessed by separating the index with a dot instead of using casual array access syntax.
- Changed: Reworked reference resolver to work in a recursive manner
- Changed: Update documentation

- Added: Option to resolve list of dicts
- Bugfix: Accessing elements of dictionaries passed as include parameters now work properly.


Version 0.2.0, 2023-08-18
-----------------------

- Bugfix: Syntax error
- Added: Inline Loop feature. Strings can now be extended using loops.
- Changed: accepting absolute filepaths now.

Version 0.1.0, 2023-08-17
-----------------------

- Bugfix: Boolean values are not parsed correctly when set in include parameters.
- Changed: Numeric values for arithmetic operations are now parsed strictly.
- Changed: Improved README documentation.
- Added: For loops will now accept multiple iterator statements and create permutations for it.

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
