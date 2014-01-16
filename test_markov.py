#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import unittest

from markov import *


class TestMarkov(unittest.TestCase):
    
    def test_init(self):
        m = Markov()
        self.assertIsInstance(m, Markov)
        self.assertEqual(m.order, 1)

        m = Markov(order=2)
        self.assertEqual(m.order, 2)

    def test_init_errors(self):
        self.assertRaises(ValueError, Markov, 0)
        self.assertRaises(ValueError, Markov, -1)
        self.assertRaises(TypeError, Markov, 2.5)


    def test_add_errors(self):
        m = Markov()
        self.assertRaises(TypeError, m.add, 5)


    def test_add_order_1(self):
        m = Markov()
        m.add([1, 2, 3, 4, 5])

        self.assertIn(Markov.start, m.chains[0])
        self.assertIn(1, m.chains[0])
        self.assertIn(2, m.chains[0])
        self.assertIn(3, m.chains[0])
        self.assertIn(4, m.chains[0])
        self.assertIn(5, m.chains[0])

        self.assertIn(Markov.end, m.chains[1])
        self.assertIn(5, m.chains[1])
        self.assertIn(4, m.chains[1])
        self.assertIn(3, m.chains[1])
        self.assertIn(2, m.chains[1])
        self.assertIn(1, m.chains[1])

        self.assertEqual(m.chains[0][Markov.start], {(1,): 1})
        self.assertEqual(m.chains[0][1], {(2,): 1})
        self.assertEqual(m.chains[0][2], {(3,): 1})
        self.assertEqual(m.chains[0][3], {(4,): 1})
        self.assertEqual(m.chains[0][4], {(5,): 1})
        self.assertEqual(m.chains[0][5], {(Markov.end,): 1})
        
        self.assertEqual(m.chains[1][Markov.end], {(5,): 1})
        self.assertEqual(m.chains[1][5], {(4,): 1})
        self.assertEqual(m.chains[1][4], {(3,): 1})
        self.assertEqual(m.chains[1][3], {(2,): 1})
        self.assertEqual(m.chains[1][2], {(1,): 1})
        self.assertEqual(m.chains[1][1], {(Markov.start,): 1})

    def test_add_order_2(self):
        m = Markov(order=2)
        m.add([
            1,
            1, 2,
            1, 2, 3,
            1, 2, 3, 4,
            1, 2, 3, 4, 5])

        self.assertEqual(m.chains[0][Markov.start], {(1, 1): 1})
        self.assertEqual(m.chains[0][1],
                         {(1, 2): 1, (2, 1): 1, (2, 3): 3})
        self.assertEqual(m.chains[0][2],
                         {(1, 2): 1, (3, 1): 1, (3, 4): 2})
        self.assertEqual(m.chains[0][3],
                         {(1, 2): 1, (4, 1): 1, (4, 5): 1})
        self.assertEqual(m.chains[0][4],
                         {(1, 2): 1, (5, Markov.end): 1})
        self.assertEqual(m.chains[0][5], {(Markov.end,): 1})

        self.assertEqual(m.chains[1][Markov.end], {(5, 4): 1})
        self.assertEqual(m.chains[1][5], {(4, 3): 1})
        self.assertEqual(m.chains[1][4], {(3, 2): 2})
        self.assertEqual(m.chains[1][3], {(2, 1): 3})
        self.assertEqual(m.chains[1][2],
                         {(1, 4): 1, (1, 3): 1, (1, 2): 1, (1, 1): 1})
        self.assertEqual(m.chains[1][1],
                         {(4, 3): 1, (3, 2): 1, (2, 1): 1,
                          (1, Markov.start): 1, (Markov.start,): 1})


    def test_choices_order_1(self):
        m = Markov()
        m.add([1, 2, 3, 4, 5])

        self.assertEqual(m.choices([Markov.start]), {(1,): 1})
        self.assertEqual(m.choices([1]), {(2,): 1})
        self.assertEqual(m.choices([2]), {(3,): 1})
        self.assertEqual(m.choices([3]), {(4,): 1})
        self.assertEqual(m.choices([4]), {(5,): 1})
        self.assertEqual(m.choices([5]), {(Markov.end,): 1})
        
        self.assertEqual(m.choices([Markov.end], 'backward'), {(5,): 1})
        self.assertEqual(m.choices([5], 'backward'), {(4,): 1})
        self.assertEqual(m.choices([4], 'backward'), {(3,): 1})
        self.assertEqual(m.choices([3], 'backward'), {(2,): 1})
        self.assertEqual(m.choices([2], 'backward'), {(1,): 1})
        self.assertEqual(m.choices([1], 'backward'), {(Markov.start,): 1})

    def test_choices_order_2(self):
        m = Markov(order=2)
        m.add([
            1,
            1, 2,
            1, 2, 3,
            1, 2, 3, 4,
            1, 2, 3, 4, 5])

        self.assertEqual(m.choices([Markov.start, 1]), {(1,): 1})
        self.assertEqual(m.choices([1, 1]), {(2,): 1})
        self.assertEqual(m.choices([1, 2]), {(1,): 1, (3,): 3})
        self.assertEqual(m.choices([2, 1]), {(2,): 1})
        self.assertEqual(m.choices([2, 3]), {(1,): 1, (4,): 2})
        self.assertEqual(m.choices([3, 1]), {(2,): 1})
        self.assertEqual(m.choices([3, 4]), {(1,): 1, (5,): 1})
        self.assertEqual(m.choices([4, 1]), {(2,): 1})
        self.assertEqual(m.choices([4, 5]), {(Markov.end,): 1})

    def test_choices_errors(self):
        m = Markov()
        m.add([1, 2, 3, 4, 5])
        self.assertRaises(TypeError, m.choices, 5)
        self.assertRaises(ValueError, m.choices, [1], direction='sideways')
        self.assertRaises(IndexError, m.choices, [])


if __name__ == '__main__':
    unittest.main()
