from setuptools import setup

setup(
    name='algoraphics',
    author='Dan Munro',
    install_requires=[
        'cairosvg',
        'matplotlib',
        'moviepy',
        'numpy',
        'Pillow',
        'Rtree',
        'scikit-image',
        'scipy',
        'Shapely',
        'typing',
    ],
    extras_require={
        'tests': [
        ],
        'docs': [
            'sphinx',
            'sphinx_autodoc_typehints',
        ]
    }
)
