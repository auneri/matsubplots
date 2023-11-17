# matsubplots Release Instructions

1. Create a new tag
    * update `__version__` and `CHANGELOG` with commit message "Release vX.X.X"
    * add tag with message "Release vX.X.X"
    * push changes to [matsubplots](https://github.com/auneri/matsubplots)

2. Upload new package to PyPI

    ```bash
    git clone --depth 1 --branch vX.X.X https://github.com/auneri/matsubplots src
    conda create --yes --prefix ./env python=3.10 setuptools
    conda activate ./env
    cd src
    python setup.py sdist bdist_wheel
    conda activate base
    twine upload dist/*
    ```
