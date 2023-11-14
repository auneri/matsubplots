import inspect
import pathlib

import setuptools


def read(filename):
    filepath = pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent / filename
    with filepath.open() as f:
        return f.read()


setuptools.setup(
    name='matsubplots',
    description='Better subplots for matplotlib.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://auneri.github.io/matsubplots',
    author='Ali Uneri',
    license='MIT',
    license_files=('LICENSE.md',),
    classifiers=[
        'Framework :: Matplotlib',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'],
    packages=setuptools.find_packages(),
    install_requires=[
        'matplotlib'],
    python_requires='>=3.7')
