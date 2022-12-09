===============================================================================
yaml-extender
===============================================================================

Description
-------
Extends the common .yaml syntax to provide more complex configuration options

References
-------

Yaml values can be referenced by using ``{{ref}}``
Additionally a default value can be given using a colon symbol withint he reference ``{{ref:default}}``

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


Also you can use default


Includes
-------

Yaml files can include other .yaml files by using the ``xyml.include: file.yaml`` statement.
Additionally all reference values within the included file can be overwritten using parameters.
Parameters are contained within the include statement ``xyml.include: file.yaml<<my_ref=param1>>``

Example
~~~~~~

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
-------

tbd
