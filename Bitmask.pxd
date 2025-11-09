from libc.stdint cimport uint32_t, uint64_t

cdef int MODE_32
cdef int MODE_64
cdef int MODE_PY

cdef class Bitmask:
    cdef public int n
    cdef public int mode
    cdef uint32_t mask32
    cdef uint64_t mask64
    cdef Py_ssize_t maskpy

    cpdef set to_set(self)
    cpdef int count(self)