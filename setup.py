from setuptools import setup

setup(
    name='algoraphics',
    # (...)
    install_requires=[
        'matplotlib'
        'scipy'
        'Shapely'
        'Rtree'
        'numpy'
        'scikit-image'
        'Pillow'
        'typing'],
    extras_require={
        'tests': [
        ],
        'docs': [
            'sphinx',
            'sphinx_autodoc_typehints']}
)
