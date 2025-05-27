"""
pylightlib.msc.Singleton
========================

Provides a metaclass implementation of the Singleton design pattern.

Author:
    Corvin Gröning

Date:
    2025-03-21

Version:
    0.1

This module defines a `Singleton` metaclass, which ensures that a class has only
one instance throughout the lifetime of the application.

Usage example:

```
class SomeClass(metaclass=Singleton):
    def __init__(self):
        ...
```

Once defined with this metaclass, all instantiations of `SomeClass` will return
the same object.

Features:

- Enforces a single instance per class.
- Accessible instance via the `instance` property.

"""

class Singleton(type):
    """
    Metaclass for the singleton pattern.

    Usage example:

        class SomeClass(metaclass=Singleton):
            def __init__(self):
                ...
    """

    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

    @property
    def instance(self):
        return self._instance
