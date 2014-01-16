# -*- coding: utf-8 -*-

from collections import defaultdict, Counter
from itertools import chain

class Markov(object):

    class Endpoint(object):
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return '<%s: %s>' % (self.__class__.__name__, self.name)
    
    start = Endpoint('start')
    end = Endpoint('end')
    directions = ('forward', 'backward')
    
    def __init__(self, order=1):
        if not isinstance(order, int):
            raise TypeError('order must be int')
        if order < 1:
            raise ValueError('order must be 1 or higher')

        self.order = order
        self.chains = [defaultdict(Counter) for d in Markov.directions]

    def __padded_sequences(self, sequence):
        """
        Yield a list containing the sequence padded with start and end markers,
        then the same sequence in reverse.  Used to generate the two lists
        on the fly without eating up memory.
        """
        start, end = [Markov.start], [Markov.end]
        yield list(chain(start, sequence, end))
        yield list(chain(end, reversed(sequence), start))

    def add(self, sequence):
        """
        Add a sequence of elements to the Markov chain.
        """
        for d, padded_sequence in enumerate(self.__padded_sequences(sequence)):
            for e, element in enumerate(padded_sequence):
                if e == 0 or not isinstance(element, Markov.Endpoint):
                    subseq = tuple(padded_sequence[e+1 : e+1+self.order])
                    self.chains[d][element][subseq] += 1
    
    def choices(self, sequence, direction='forward'):
        """
        Get a dict that maps possible subsequent states to their respective
        weights.

        Given an nth-order Markov chain and a sequence of length 1, the map's
        keys will be sequences of length n.  Given a sequence of length s, the
        map's keys will be sequences of length (n - min(n, s) + 1).

        If the direction is 'backward', the sequence is evaluated in reverse
        order.  For most practical purposes, this means the caller does not
        need to modify the sequence prior to searching for backward choices.
        """
        choices = {}
        d = Markov.directions.index(direction)
        # 'Normalize' the sequence if we're going backwards.
        if direction == 'backward':
            sequence = list(reversed(sequence))
        # The 'starting' element is the `order`th-from-last element, or the
        # first element if the sequence length is less than the order. The
        # subsequence of elements after this starting point will be compared.
        element_index = max(0, len(sequence) - self.order)
        element = sequence[element_index]
        subseq = tuple(sequence[element_index+1:])
        # Compare the subsequence to the first `order`-minus-one elements or
        # the first sequence-length-minus-one elements, whichever is lower.
        choice_index = min(self.order, len(sequence)) - 1
        for choice, weight in self.chains[d][element].iteritems():
            if choice[:choice_index] == subseq:
                # We're only interested in the elements that weren't given in
                # the original sequence, so slice the choice before using it
                # as a key.
                choices[choice[choice_index:]] = weight
        return choices
