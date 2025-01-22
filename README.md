# matsubplots

Better subplots for [matplotlib](https://matplotlib.org).

[![license](https://img.shields.io/github/license/auneri/matsubplots)](https://github.com/auneri/matsubplots/blob/main/LICENSE.md)
[![build](https://img.shields.io/github/actions/workflow/status/auneri/matsubplots/main.yml)](https://github.com/auneri/matsubplots/actions)
[![pypi](https://img.shields.io/pypi/v/matsubplots)](https://pypi.org/project/matsubplots)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/matsubplots)](https://anaconda.org/conda-forge/matsubplots)

## Getting started

Install using `pip install matsubplots` or `conda install -c conda-forge matsubplots`.

See [example notebooks](https://github.com/auneri/matsubplots/tree/main/examples) for basic instructions.

## Releasing a new version

1. Update `project.version` in `pyproject.toml` and `CHANGELOG` with commit message "Release vX.X.X".
2. Add tag vX.X.X with message "Release vX.X.X".
3. Push the tag and create a new release on [matsubplots](https://github.com/auneri/matsubplots).
4. Merge the auto-generated pull request on [matsubplots-feedstock](https://github.com/conda-forge/matsubplots-feedstock).
