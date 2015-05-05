#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_fuzzyraft
----------------------------------

Tests for `fuzzyraft` module.
"""

import unittest

from fuzzyraft import fuzzyraft


class TestFuzzyraft(unittest.TestCase):
    def test_node_initial_state_is_follower(self):
        node = fuzzyraft.Node()
        self.assertEquals(node.state, fuzzyraft.State.FOLLOWER)

if __name__ == '__main__':
    unittest.main()
