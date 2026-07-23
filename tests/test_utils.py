"""Tests for pylightlib.msc.Utils."""

import pytest
from pylightlib.msc.Utils import Utils


class TestNextIndex:
    """Tests for Utils.next_index."""

    def test_forward_normal(self):
        assert Utils.next_index(2, 5, direction=1, loop_behavior=True) == 3

    def test_backward_normal(self):
        assert Utils.next_index(2, 5, direction=-1, loop_behavior=True) == 1

    def test_wrap_forward(self):
        assert Utils.next_index(4, 5, direction=1, loop_behavior=True) == 0

    def test_wrap_backward(self):
        assert Utils.next_index(0, 5, direction=-1, loop_behavior=True) == 4

    def test_clamp_forward(self):
        assert Utils.next_index(4, 5, direction=1, loop_behavior=False) == 4

    def test_clamp_backward(self):
        assert Utils.next_index(0, 5, direction=-1, loop_behavior=False) == 0

    def test_length_one_loop(self):
        assert Utils.next_index(0, 1, direction=1, loop_behavior=True) == 0

    def test_length_one_clamp(self):
        assert Utils.next_index(0, 1, direction=1, loop_behavior=False) == 0

    def test_forward_mid_list_clamp(self):
        assert Utils.next_index(2, 5, direction=1, loop_behavior=False) == 3

    def test_backward_mid_list_clamp(self):
        assert Utils.next_index(2, 5, direction=-1, loop_behavior=False) == 1
