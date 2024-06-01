from setuptools import setup, find_packages

setup(
    name='saxs',
    version='1.0.0',
    packages=find_packages(),
    author='Isai Gordeev',
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'torch'
    ],
)