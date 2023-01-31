===============================================================================
yaml-extender
===============================================================================

Description
-----------
Extends the common .yaml syntax to provide more complex configuration options.
The yaml_extender can be used to resolve the extended yaml syntax as shown in Usage.rst.
The following options for extended yaml syntax are available.

References
----------

Yaml values can be referenced by using ``{{ref}}``
Additionally a default value can be given using a colon symbol within the reference ``{{ref:default}}``

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

    ref_val_1: "{{dict_1.subvalue_2[0].config}}"
    ref_val_2: "{{dict_1.subvalue_2[1].path}}"
    ref_val_3: "{{dict_1.subvalue_2[2].path:default_value}}"
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


Also you can use default values by giving a value separated by a colon.
Example::

    ref_val_1: {{ not_existing:123 }}

results in::

    ref_val_1: 123

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
      - file1.yaml
      - file2.yaml

file1.yaml::

    subvalue_2: 123
    subvalue_3: 456

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

