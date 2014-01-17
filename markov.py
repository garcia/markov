# -*- coding: utf-8 -*-
import abc
from collections import *
from itertools import chain

class AbstractMarkov(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def element_count(self): pass
    @abc.abstractmethod
    def elements(self): pass
    @abc.abstractmethod
    def add(self, sequence): pass
    @abc.abstractmethod
    def choices(self, sequence, direction='forward'): pass


class Markov(object):
    """
    This class represents an nth-order Markov chain.  Sequences of elements
    are processed such that each element is assigned a probability of being
    preceded or succeeded by a sequence of n elements.
    """

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
    
    def element_count(self):
        """
        Get the number of unique elements stored, including the start and end
        markers.
        """
        return len(self.chains[0])

    def elements(self):
        """
        Get a list of all elements stored, including the start and end markers.
        """
        return self.chains[0].keys()

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
        # Optimization: don't create an empty Counter if none exists here.
        if element not in self.chains[d]:
            return choices
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

AbstractMarkov.register(Markov)


class CompositeMarkov(object):
    """
    This class implements the same interface as Markov, but manages multiple
    Markov instances that expire after a certain number of add operations.
    Read operations (e.g. the `elements` and `choices` methods) combine output
    from all of the instances; write operations (`add`) only write to the most
    recently created instance.
    """
    
    def __init__(self, max_instances, max_elements, order=1):
        self.max_instances = max_instances
        self.max_elements = max_elements
        self.order = order
        self.instances = deque()
        self._add_instance()

    def __element_set(self):
        """
        Get a set of all elements across all stored Markov instances. Used
        internally by `element_count` and `elements`.
        """
        return set(chain.from_iterable(instance.elements()
            for instance in self.instances))

    def element_count(self):
        """
        Get the number of unique elements across all stored Markov instances.
        """
        return len(self.__element_set())
    
    def elements(self):
        """
        Get a list of all unique elements across all stored Markov instances.
        """
        return list(self.__element_set())

    def __add_instance(self):
        """
        Add a new Markov instance to the start of the list.
        """
        self.instances.appendleft(Markov(self.order))

    def add(self, *args, **kwargs):
        """
        Add a sequence of elements to the first Markov chain.

        If this pushes the element count over the maximum, a new Markov chain
        is added to the instance stack.  If that pushes the instance count
        over the maximum, the oldest Markov chain is removed from the bottom of
        the stack.
        """
        self.instances[0].add(*args, **kwargs)
        if self.instances[0].element_count() > self.max_elements:
            self.__add_instance()
        if len(self.instances) > self.max_instances:
            self.instances.pop()

    def choices(self, *args, **kwargs):
        """
        Get a dict that maps possible subsequent states to their respective
        weights.

        This merges the choices given by each Markov instance using a Counter.
        """
        choices = Counter()
        for instance in self.instances:
            choices.update(instance.choices(*args, **kwargs))
        return dict(choices)

AbstractMarkov.register(CompositeMarkov)
