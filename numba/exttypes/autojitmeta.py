# -*- coding: utf-8 -*-

"""
Autojit meta class.
"""

from __future__ import print_function, division, absolute_import

class _AutojitMeta(type):
    """
    Metaclass base for autojit classes.
    """

def create_unspecialized_cls(py_class, class_specializer):
    """
    Create an unspecialized class.

    class_specializer:
        NumbaSpecializingWrapper (args -> specialized object instance)
    """

    class AutojitMeta(_AutojitMeta, type(py_class)):
        """
        Metaclass base for autojit classes.

            AutojitMeta -> UnspecializedClass -> SpecializedInstance
        """

        def __call__(cls, *args, **kwargs):
            return class_specializer(*args, **kwargs)

        def __getitem__(cls, key):
            assert isinstance(key, dict)

            for specialized_cls in cls.specializations:
                attrdict = specialized_cls.exttype.attribute_table.attributedict
                if attrdict == key:
                    return specialized_cls

            raise KeyError(key)

        @property
        def specializations(cls):
            return class_specializer.funccache.specializations.values()


    return AutojitMeta(py_class.__name__,
                       py_class.__bases__,
                       dict(vars(py_class)))


def create_specialized_metaclass(py_class):
    """
    When the autojit cache compiles a new class specialization, it invokes
    it with the constructor arguments. Since A_specialized inherits from A,
    AutojitMeta.__call__ again tries to specialize the class. We need to
    override this behaviour and instead instantiate A_specialized through
    type.__call__ (invoking A_specialized.{__new__,__init__}).
    """

    class SpecializedMeta(type(py_class)):
        def __call__(cls, *args, **kwargs):
            return type.__call__(cls, *args, **kwargs)

    return SpecializedMeta


if __name__ == '__main__':
    from numba import *

    @autojit
    class C(object):
        def __init__(self, value):
            self.value = value

    obj = C(10.0)
    print(type(obj).exttype)

    specialized_cls = C[{'value': double}]
    print(specialized_cls, C, specialized_cls is C)

    assert issubclass(specialized_cls, C)
    assert isinstance(obj, C)