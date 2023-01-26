From CLI
-----------

The yaml_extender can be used from command line using::

    python -m yaml_extender <input> <output> [parameters]

input: Path to the input file containing extended yaml syntax.
output: Path to the output file.
parameters: Additional parameters, which can be referenced in the extended yaml syntax. See Parameters :ref:`parameters`.

**Example**::

    python -m yaml_extender path/to/input.xyml /path/to/output.yml --my_param1 123 --my_param2 abc


As Python module
----------------

You can also use yaml_extender from within you within your python scripts.
Additional parameters for syntax resolution (See Parameters :ref:`parameters`.) can be provided as dictionary, when creating the XYmlFile.

Example::

    from yaml_extender import XYmlFile

    file = XYmlFile("/usr/me/my/file.xyml", {"my_param1": 123, "my_param2": "abc"})
    print(file.content)
    file.save("/usr/me/my/processed.xyml")
