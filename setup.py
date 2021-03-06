from setuptools import setup

setup(
    name='algoraphics',
    author='Dan Munro',
    varsion='1.0',
    packages=['algoraphics', 'algoraphics.extras'],
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
            'sphinx_rtd_theme',
            'sphinx_autodoc_typehints',
        ]
    }
)
