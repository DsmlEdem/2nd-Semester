# This code is taken from the laboratory of "Stochastic Processes" course of ECE NTUA 6th semester, Prof. Loulakis
from bisect import bisect_left
from random import random

import networkx as nx  # get communication classes
import numpy as np
from scipy.sparse# This code is taken from the laboratory of "Stochastic Processes" course of ECE NTUA 6th semester, Prof. Loulakis
from bisect import bisect_left
from random import random

import networkx as nx  # get communication classes
import numpy as np
from scipy.sparse import csr_matrix


class markov_chain:

    def __init__(self, markov_table, init_dist=None):
        """
        Constructs a Markov Chain from a transition matrix.
        The initial distribution can be provided or setted aftewards.
        """

        # Attributes
        self.running_state = None
        self.steps = 0
        self.visits = {state: 0 for state in markov_table}
        size = len(markov_table)

        # Set up state transition probs
        self._states = {state: self._partial_sums(dist)
                        for state, dist in markov_table.items()}
        for state, dist in self._states.items():
            if not np.isclose(dist[-1][0], 1.0):
                msg = "State {} transitions do not add up to 1.0".format(state)
                raise ValueError(msg)
        self._probs_state = np.array([0] * size)

        # Adjacency Matrix
        data, rows, cols = [], [], []
        for row, dist in markov_table.items():
            col, pval = zip(*[(s, p) for s, p in dist.items() if p > 0])
            rows += [row] * len(col)
            cols += col
            data += pval
        # make sure they are in the right order
        enum = {state: i for i, state in enumerate(self._states)}
        rows = [enum[r] for r in rows]
        cols = [enum[c] for c in cols]
        self._adj = csr_matrix((data, (rows, cols)), shape=(size, size))

        # Communication Classes
        classes = {'Closed': [], 'Open': []}
        g = nx.MultiDiGraph(self._adj)
        scc = list(nx.strongly_connected_components(g))
        g = nx.condensation(g)  # SCCs collapse to single nodes
        for n in g:
            if g.out_degree(n) == 0:
                classes["Closed"].append(scc[n])
            else:
                classes["Open"].append(scc[n])
        self.communication_classes = classes

        # Set Initial State
        self._init_dist = None
        if init_dist is not None:
            self.init_dist = init_dist

    def __len__(self):
        """The cardinality of the state-space"""
        return len(self._states)

    @property
    def probs_matrix(self):
        """The transition probability matrix"""
        return self._adj.toarray()

    @property
    def probs_state(self):
        """
        Computes analytically the probability of being in every state at
        currentn step. Returns a vector of state probabilities
        """
        init_dist = np.array([self.init_dist.get(state, 0.0)
                              for state in self._states])
        probs = init_dist @ (self._adj ** self.steps)
        return dict(zip(self._states, probs))

    @property
    def init_dist(self):
        """The initial distribution of the chain"""
        return self._init_dist

    @init_dist.setter
    def init_dist(self, dist):
        if not np.isclose(sum(dist.values()), 1.0):
            msg = "The transition probabilities of init_dist must add up to 1.0"
            raise ValueError(msg)
        self._init_dist = dist
        self._state0 = self._partial_sums(dist)
        self.running_state = None

    @property
    def eigenvalues(self):
        """Returns the eigenvalues of the transition table"""
        return list(np.sort(np.linalg.eigvals(self.probs_matrix)))

    def _partial_sums(self, dist):
        """
        Takes as input a row of the probability matrix (dist)
        and generates its partial sums.
        These are cached as tuples (sum, state) to be sampled.
        """
        states, probs = zip(*[(s, p) for s, p in dist.items() if p > 0])
        probs = np.cumsum(probs)
        return list(zip(probs, states))

    def _next_state(self, state):
        """Selects a new state based on the transition probabilities"""
        return state[bisect_left(state, (random(), ))][1]

    def start(self):
        """First step of the chain choosen from the initial distribution"""

        # Initiate walk
        self.steps = 0
        for state in self._states:
            self.visits[state] = 0

        # Initialize the state distribution - to be updated as we walk
        self.running_state = self._next_state(self._state0)
        self.visits[self.running_state] = 1

    def move(self):
        """Moves to the next state and updates all relevant fields"""
        transition_probs = self._states[self.running_state]
        self.running_state = self._next_state(transition_probs)
        self.steps += 1
        self.visits[self.running_state] += 1
