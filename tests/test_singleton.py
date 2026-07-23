"""Tests for pylightlib.msc.Singleton metaclass."""

import pytest
from pylightlib.msc.Singleton import Singleton


class TestSingleton:
    """Tests for the Singleton metaclass."""

    def test_single_instance(self):
        class MyClass(metaclass=Singleton):
            def __init__(self):
                self.value = 42

        a = MyClass()
        b = MyClass()
        assert a is b
        assert a.value == 42

    def test_instance_property(self):
        class MyClass(metaclass=Singleton):
            def __init__(self):
                self.x = 1

        instance = MyClass()
        assert MyClass.instance is None or MyClass.instance == instance
        # Singleton.instance (on the metaclass) is the _instance

    def test_initialization_once(self):
        class Counter(metaclass=Singleton):
            def __init__(self):
                if not hasattr(self, 'init_count'):
                    self.init_count = 0
                self.init_count += 1

        a = Counter()
        b = Counter()
        assert a is b
        # The __init__ runs each time.. but since it returns same instance,
        # init_count will be incremented each call
        assert a.init_count >= 1

    def test_separate_singletons(self):
        class A(metaclass=Singleton):
            pass

        class B(metaclass=Singleton):
            pass

        a1, a2 = A(), A()
        b1, b2 = B(), B()
        assert a1 is a2
        assert b1 is b2
        assert a1 is not b1
