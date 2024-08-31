# distutils: language = c++
# Adapted from https://github.com/kilian-gebhardt/MinMaxHeap

from libcpp.vector cimport vector

cdef extern from "_minmaxheap.h" namespace "minmaxheap":
	cdef struct astar_t:
		double augment;
		double dist;
		int curnode;
		int parent;

	cdef struct dijkstra_t:
		double act_wt;
		int act_nod;

	cdef cppclass MinMaxHeap[T]:
		MinMaxHeap()
		# MinMaxHeap(size_t reserve)
		# short level(size_t n)
		size_t size()
		void insert(T key)
		void clear()
		T peekmin()
		T peekmax()
		T popmin()
		T popmax()
		void reserve(size_t n)
		vector[T] getheap()
