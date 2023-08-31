===============================================================================
yaml-extender
===============================================================================

.. contents:: :local:


Description
-----------
Extends the common .yaml syntax to provide more complex configuration options.
The yaml_extender can be used to resolve the extended yaml syntax as shown in Usage.rst.
The following options for extended yaml syntax are available.

For more examples on how to use, check the unittests in tests/ directory.

References
----------

Yaml values can be referenced by using ``{{ref}}``
More specific values from dictionaries can be accessed by separating references with a dot  ``{{ref.subref}}``
You can access array elements by specifying the index separated by a dot. ``{{ref.1}}``

**Simple Example**::

    my_reference: test_value
    my_path: path/to/my/{{ my_reference }}
    copy_reference: "{{my_reference}}"
    my_config: path/to/{{ configured_value:default.cfg }}

Results in::

    my_reference: test_value
    my_path: path/to/my/test_value
    copy_reference: test_value
    my_config: path/to/default.cfg

More complex references can be done using dictionaries as well as lists.

**Complex Example**::

    ref_val_1: "{{dict_1.subvalue_2.0.config}}"
    ref_val_2: "{{dict_1.subvalue_2.1.path}}"
    ref_val_3: "{{dict_1.subvalue_2.2.path:default_value}}"
    dict_1:
      subvalue_1: const_val
      subvalue_2:
      - path: first/path
        config: first.cfg
      - path: second/path
        config: second.cfg

Results in::

    ref_val_1: first.cfg
    ref_val_2: second/path
    ref_val_3: default_value
    dict_1:
      subvalue_1: const_val
      subvalue_2:
      - path: first/path
        config: first.cfg
      - path: second/path
        config: second.cfg


Additionally a default value can be given using a colon symbol within the reference ``{{ref:default}}``
Example::

    ref_val_1: {{ not_existing:123 }}

results in::

    ref_val_1: 123

Lists
~~~~~

When accessing lists without specifying an index, they will automatically get joined together with a whitespace.

Example::

    array_1:
    - a
    - b
    - c
    ref_val_1: {{ array_1 }}

results in::

    array_1:
    - a
    - b
    - c
    ref_val_1: a b c

This can be done similar with list of dictionaries::

    array_1:
    - first: a
      second: 1
    - first: b
      second: 2
    firsts: {{array_1.first}}
    seconds: {{array_1.second}}

Resulting in::

    array_1:
    - first: a
      second: 1
    - first: b
      second: 2
    firsts: a b
    seconds: 1 2

Environment variables
~~~~~~~~~~~~~~~~~~~~~

In extended yaml syntax environment variables can be referenced using the key ``xyml.env``.

An Environment ENV_VAR variable can be referenced like this::

    my_value: echo environment variable = {{ xyml.env.ENV_VAR}}


.. _parameters:

Parameters
~~~~~~~~~~
In extended yaml syntax additional parameters can be referenced using the key ``xyml.param``.

When including yaml_extender in another python script the parameters can be passed as dictionary when creating a XYmlFile object.
When using yaml_extender over command line all named parameters will be used to resolve ``xyml.param`` statements.

**Warning**
Only named parameters are allowed, positional arguments will cause problems.

An parameter given as "--my_param 123" or {"my_param": 123} can be referenced like this::

    my_value: echo This is a parameter {{ xyml.param.my_param }}


Includes
--------

Yaml files can include other .yaml files by using the ``xyml.include: file.yaml`` statement.
Additionally all reference values within the included file can be overwritten using parameters.
Parameters are contained within the include statement ``xyml.include: file.yaml<<my_ref=param1>>``

Example
~~~~~~~

root.yaml::

    ref_1: value1
    dict_1:
      subvalue_1: abc
      xyml.include:
      - file1.yaml<<ref_1=456>>
      - file2.yaml

file1.yaml::

    subvalue_2: 123
    subvalue_3: {{ref_1}}

file2.yaml::

    subvalue_4:
    - abc
    - xyz

**Results in**::

    ref_1: value1
    dict_1:
      subvalue_1: abc
      subvalue_2: 123
      subvalue_3: 456
      subvalue_4:
      - abc
      - xyz


**Note:**
It is also allowed to use ref values within include paths like this::

    my_dir: path/to/my/dir
    xyml.include: "{{my_dir}}/inc.yaml"


For loops
---------

Certain entries in your config can be repeated based on array values in you config.
You can directly repeat dictionary values by adding a ``xyml.loop`` statement.
Of course subvalues can be accessed in the same way as in normal references.

**Example:**::

    array_1:
    - value: abc
      path: first/path
    - value: xyz
      path: second/path

    commands:
      xyml.for: iterator:array_1
      cmd: sh {{ iterator.value }}
      from: "{{ iterator.path }}"


will result in::

    array_1:
    - value: abc
      path: first/path
    - value: xyz
      path: second/path

    commands:
    - cmd: sh abc
      from: first/path
    - cmd: sh xyz
      from: second/path



Flat Loops
~~~~~~~~~~
Loops can also flatten itself. If you want to repeat arrays you can use the keyword ``xyml.content`` to provide the content of the loop.

**Example**::

    array_1:
    - abc
    - xyz
    commands:
      xyml.for: iterator:array_1
      xyml.content:
      - cmd: sh {{ iterator }}
      - cmd: echo {{ iterator }}

Will result in::

    array_1:
    - abc
    - xyz
    commands:
      - cmd: sh abc
      - cmd: echo abc
      - cmd: sh xyz
      - cmd: echo xyz


Loops for Permutation
~~~~~~~~~~~~~~~~~~~~~

Loops can also be used to create permutations. To simplify that a loop statement can take a custom amount of iterators.

**Example**::

    array_1:
    - abc
    - xyz
    array_2:
    - 123
    - 456
    commands:
      xyml.for: i:array_1, j:array_2
      xyml.content:
      - cmd: sh {{ i }} {{ j }}

Will result in::

    array_1:
    - abc
    - xyz
    array_2:
    - 123
    - 456
    commands:
      - cmd: sh abc 123
      - cmd: sh abc 456
      - cmd: sh xyz 123
      - cmd: sh xyz 456

Inline Loops
~~~~~~~~~~~~~~~~~~~~~

You can also use loops to improve the string values in your configuration.
This can be used to simplify reoccurring values like parameters.

**Example**::

    array_1:
    - abc
    - xyz
    command: Input parameters: {{xyml.for:param:array_1:-i {{param}}}}

Will result in::

    array_1:
    - abc
    - xyz
    command: Input parameters: -i abc -i xyz
