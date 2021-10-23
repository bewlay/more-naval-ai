"""
An algorithm "solving" the travelling salesperson problem (TSP).
The algorithm repeatedly chooses a random subsequence, and reverses it if this improves the cost of the tour.
If many consecutive random attempts are unsuccessful, it does a single deterministic step, where each possible sub-
sequences is checked. The algorithm runs for a given number of steps, or until a deterministic step makes no changes.

Results can be arbitrarily bad. This is expected, since TSP cannot be approximated up to a constant factor, unless P=NP.
"""

import random


class TSPSolver :
	def __init__( self, items, weights, cyclic, seed ) :
		"""
		Construct a TSPSolver.
		:param items: The collection of items (vertices in a complete graph).
		:param weights: The "distances" between any two items (edge weights). Maps (Item, Item) tuples to ints or floats
			Must be symmetric, but does not have to satisfy the triangle inequality.
		:param cyclic: Whether to find a small-weight cycle or a small-weight path.
		:param seed: The seed for random decisions.
		"""
		self._items = list( items )
		self._n = len( items )
		self._weights = weights
		self._cyclic = cyclic
		self._rand = random.Random( seed )
		self._switch_threshold = self._n # After how many unsuccessfull randomized tries we try a deterministic step

	def seq_weight( self, seq ) :
		"""
		The weight of the given sequence. If not in cyclic mode, this is simply the sum of the weights between adjacent
		elements in the sequence. If in cyclic mode, add the weight between the first and last element.
		"""
		result = 0
		for i in range( len( seq ) - (1 - int(self._cyclic) ) ) :
			result += self._weights[ seq[i], seq[(i+1) % self._n] ]
		return result

	def _reverse_part( self, seq, start, end  ) :
		for i in range( 0, (end-start+1) // 2 ) :
			j = (start+i) % self._n
			k = (end-i) % self._n
			seq[j], seq[k] = seq[k], seq[j]

	def _should_reverse_part( self, seq, start, end ) :
		after_end = (end+1) % self._n
		if start == after_end :
			return False
		assert self._cyclic or start < end
		increment = 0
		if start > 0 or self._cyclic :
			increment += self._weights[ seq[start-1], seq[end] ] - self._weights[ seq[start-1], seq[start] ]
		if end < len( seq ) - 1 or self._cyclic :
			increment += self._weights[ seq[start], seq[after_end] ] - self._weights[ seq[end], seq[after_end] ]
		return increment < 0

	def _try_reverse_part( self, seq, start, end ) :
		if self._should_reverse_part( seq, start, end) :
			self._reverse_part( seq, start, end )
			return True
		else :
			return False

	def _deterministic_step( self, seq ) :
		""" Tries to reverse all possible subsequences (with overlap). """
		reversed_something = False
		for i in range( len( seq ) ) :
			for j in range( i + 1, len( seq ) ) :
				if self._try_reverse_part( seq, i, j ) :
					reversed_something = True
		return reversed_something

	def _random_step( self, seq ) :
		""" Tries to reverse a random subsequence. """
		i = self._rand.randint( 0, len( seq ) - 1 )
		j = self._rand.randint( 0, len( seq ) - 1 )
		if i != j :
			i, j = min( i, j ), max( i, j )
			return self._try_reverse_part( seq, i, j )
		else :
			return False

	def min_tsp_hybrid_heuristic( self, max_steps ) :
		"""
		Find a small-weight sequence.
		:param max_steps: The maximum number of random steps. Deterministic steps count for multiple random steps,
		partly based on empirical values.
		:return: A sequence representing a small-weight path or cycle in the graph.
		"""
		seq = list( self._items )
		count = 0
		unsuc_random_count = 0  # Unsuccessfull random steps in a row
		expected_det_time = self._n * self._n // ( 4 - 2 * int( self._cyclic ) ) # Expected time for a deterministic step. More if cyclic
		while count < max_steps :
			if unsuc_random_count < self._switch_threshold or count + expected_det_time > max_steps :
				if not self._random_step( seq ) :
					unsuc_random_count += 1
				count += 1
			else :
				# Try a deterministic step
				if not self._deterministic_step( seq ) :
					# Nothing more to do
					break
				count += expected_det_time
		return seq
