handsome
========

Rasterizer for 2D and 3D image primitives based off of NumPy

Submodules
----------

This repository includes the following git submodules:

* **sweatervest** - Located at ``external/sweatervest``
* **phillip** - Located at ``external/phillip``

Clone with Submodules
~~~~~~~~~~~~~~~~~~~~~

To clone this repository with all submodules included::

    git clone --recursive https://github.com/bracket/handsome.git

Or if you've already cloned the repository::

    git submodule update --init --recursive

Update Submodules
~~~~~~~~~~~~~~~~~

To update submodules to the latest commit on their master branch::

    git submodule update --remote --merge

Or to update a specific submodule::

    cd external/sweatervest
    git checkout master
    git pull

    cd external/phillip
    git checkout master
    git pull
