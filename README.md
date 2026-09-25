# StatisticsLectures

[![notebooks](https://github.com/wiso/StatisticsLectures/actions/workflows/notebooks.yml/badge.svg)](https://github.com/wiso/StatisticsLectures/actions/workflows/notebooks.yml)

Material for statistics lectures for physicists.

The notebooks (files with extension .ipynb) can be opened directly on github. To render them as slides [RISE](https://github.com/jupyterlab-contrib/rise) (`jupyterlab_rise`) is used.

## Setup (recommended): micromamba

Some notebooks use [ROOT](https://root.cern) (RooFit/RooStats) and graphviz (`dot`), which are easily installed from conda-forge. With [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html):

    micromamba env create -f environment.yml

or, to get exactly the same package versions (linux-64 only):

    micromamba create -n statisticslectures -f environment.lock.txt
    micromamba env config vars set -n statisticslectures PYTHONNOUSERSITE=1

(`PYTHONNOUSERSITE=1` prevents packages installed with `pip install --user` from shadowing the ones in the environment; with `environment.yml` it is set automatically.)

Then every time you need the environment:

    micromamba activate statisticslectures

To update the environment after changing `environment.yml`, recreate it (this also applies the `variables:` section, which `micromamba env update` ignores) and regenerate the lock file:

    micromamba deactivate  # if the environment is active
    micromamba env remove -n statisticslectures
    micromamba env create -f environment.yml
    micromamba env export -n statisticslectures --explicit --md5 > environment.lock.txt

## Setup (alternative, without ROOT): virtualenv

If you don't need ROOT, a plain virtualenv is enough. Cells using ROOT/RooFit/RooStats will fail; cells calling `dot` need the system graphviz package (`sudo dnf install graphviz` or `sudo apt install graphviz`). Everything else, including the slides, works.

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

## Running the notebooks and showing the slides

    jupyter lab Lecture1.ipynb

(`jupyter notebook Lecture1.ipynb` works as well). To start the slideshow press `Alt+R` or click the RISE button in the notebook toolbar (in JupyterLab also: View → Render as slides).

In VS Code select the interpreter/kernel from the environment (e.g. `~/micromamba/envs/statisticslectures/bin/python`); VS Code can run the notebooks but does not support RISE slides.

Without RISE, static slides can be produced with

    jupyter nbconvert --to slides Lecture1.ipynb --post serve

even if the style is not optimized.
