cimport cython
from libc.stdint cimport uint32_t, uint64_t
from Bitmask cimport MODE_32, MODE_64, MODE_PY, Bitmask

# Set the constants (initialized only in .pyx)
cdef int MODE_32 = 1
cdef int MODE_64 = 2
cdef int MODE_PY = 3

cdef class Bitmask:

    def __init__(self, int n):
        self.n = n
        if n <= 32:
            self.mode = MODE_32
            self.mask32 = 0
        elif n <= 64:
            self.mode = MODE_64
            self.mask64 = 0
        else:
            self.mode = MODE_PY
            self.maskpy = 0

    @classmethod
    def from_set(cls, int n, subset):
        cdef Bitmask bm = cls(n)
        cdef int i
        if bm.mode == MODE_32:
            for i in subset:
                bm.mask32 |= 1 << (i - 1)
        elif bm.mode == MODE_64:
            for i in subset:
                bm.mask64 |= 1 << (i - 1)
        else:
            for i in subset:
                bm.maskpy |= 1 << (i - 1)
        return bm

    # ---------------------------
    # cpdef methods (exposed to C)
    cpdef set to_set(self):
        cdef int i
        cdef set s = set()
        cdef uint32_t val32
        cdef uint64_t val64
        cdef Py_ssize_t valpy

        if self.mode == MODE_32:
            val32 = self.mask32
            for i in range(self.n):
                if val32 & (1 << i):
                    s.add(i + 1)
        elif self.mode == MODE_64:
            val64 = self.mask64
            for i in range(self.n):
                if val64 & (1 << i):
                    s.add(i + 1)
        else:
            valpy = self.maskpy
            for i in range(self.n):
                if valpy & (1 << i):
                    s.add(i + 1)
        return s

    cpdef int count(self):
        cdef int i, cnt = 0
        cdef uint32_t val32
        cdef uint64_t val64
        cdef Py_ssize_t valpy

        if self.mode == MODE_32:
            val32 = self.mask32
            for i in range(self.n):
                if val32 & (1 << i):
                    cnt += 1
        elif self.mode == MODE_64:
            val64 = self.mask64
            for i in range(self.n):
                if val64 & (1 << i):
                    cnt += 1
        else:
            valpy = self.maskpy
            for i in range(self.n):
                if valpy & (1 << i):
                    cnt += 1
        return cnt

    # ---------------------------
    # Special methods — def only
    def __or__(self, Bitmask other):
        cdef Bitmask res = Bitmask(self.n)
        if self.mode == MODE_32:
            res.mask32 = self.mask32 | other.mask32
        elif self.mode == MODE_64:
            res.mask64 = self.mask64 | other.mask64
        else:
            res.maskpy = self.maskpy | other.maskpy
        return res

    def __and__(self, Bitmask other):
        cdef Bitmask res = Bitmask(self.n)
        if self.mode == MODE_32:
            res.mask32 = self.mask32 & other.mask32
        elif self.mode == MODE_64:
            res.mask64 = self.mask64 & other.mask64
        else:
            res.maskpy = self.maskpy & other.maskpy
        return res

    def __invert__(self):
        cdef Bitmask res = Bitmask(self.n)
        if self.mode == MODE_32:
            res.mask32 = (~self.mask32) & ((1 << self.n) - 1)
        elif self.mode == MODE_64:
            res.mask64 = (~self.mask64) & ((1 << self.n) - 1)
        else:
            res.maskpy = (~self.maskpy) & ((1 << self.n) - 1)
        return res

    def __eq__(self, Bitmask other):
        if self.mode == MODE_32:
            return self.mask32 == other.mask32
        elif self.mode == MODE_64:
            return self.mask64 == other.mask64
        else:
            return self.maskpy == other.maskpy

    def __bool__(self):
        if self.mode == MODE_32:
            return self.mask32 != 0
        elif self.mode == MODE_64:
            return self.mask64 != 0
        else:
            return self.maskpy != 0

    def __hash__(self):
        if self.mode == MODE_32:
            return hash(self.mask32)
        elif self.mode == MODE_64:
            return hash(self.mask64)
        else:
            return hash(self.maskpy)

    def __repr__(self):
        return f"Bitmask(n={self.n}, mode={self.mode}, bits={self.to_set()})"
