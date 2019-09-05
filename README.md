# StatisticsLectures
Material for statistics lectures for physicists.

The notebooks (files with extension .ipynb) can be opened directly on github. To render them as slides [RISE](https://github.com/damianavila/RISE) is needed. Otherwise also a simple `jupyter nbconvert --to slides Lecture1.ipynb --post serve` works, even if the style is not optimized.

To install jupyter and other software the easier way is to create a [virtualenv](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs). virtualenv can be installed with yum, dnf, apt, ... or also with pip.  Otherwise you can install the software in other ways: `sudo pip install ...` (not suggested) or just for your user (`pip install --user ...`)

    # install virtualenv, python3, pip
    virtualenv myenv
    source myenv/bin/activate
    pip install -r requirements.txt

Then everytime you need to setup the environment you should just do

    source myenv/bin/activate

To open a notebook

    jupyter notebook Lecture1.ipynb