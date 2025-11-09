# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="Bitmask",
        sources=["Bitmask.pyx"],
        language="c",
    ),
    Extension(
        name="functions",
        sources=["functions.pyx"],
        language="c",
    ),
    Extension(
        name="main",
        sources=["main.pyx"],
        language="c",
    ),
]

setup(
    name="set_cover_cython",
    ext_modules=cythonize(
        extensions,
        language_level=3,          # Python 3 syntax
        compiler_directives={
            "boundscheck": False,  # turn off bounds checking for speed
            "wraparound": False,   # turn off negative index wraparound
        },
    ),
)
