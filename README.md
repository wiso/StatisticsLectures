# StatisticsLectures
Material for statistics lectures for physicist.

The notebooks can be opened directly on github. To render them as slides [https://github.com/damianavila/RISE](RISE) is needed. Otherwise also a simple `jupyter nbconvert --to slides Lecture1.ipynb --post serve` works, even if the style is not optimized.

To install jupyter and other software the easier way is to create a [http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs](virtualenv). virtualenv can be installed with yum, dnf, apt, ... or also with pip

    virtualenv myenv
    source myenv/bin/activate
    pip install jupyter matplotlib numpy scipy

Then everytime you need to setup the environment you should just do

    source myenv/bin/activate
