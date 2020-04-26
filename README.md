# Covid-19 Analysis

## General

The analysis notebook including plots can be seen in [analysis.ipynb \[rendered\]](https://github.com/mbyt/covid-19_analysis/blob/master/analysis.ipynb).

Data sources ("*John Hopkins University*" and "*Berliner Morgenpost*") are extracted as shown in [retrieve_clean_data.ipynb \[rendered\]](https://github.com/mbyt/covid-19_analysis/blob/master/retrieve_clean_data.ipynb) and cached as [cases.csv](https://github.com/mbyt/covid-19_analysis/blob/master/cases.csv).

## Development

In order to avoid polluting the `git diff` through changed `Output[*]`
cells (especially images are problematic), the following development workflow
based on [mgeier git-jupyter](https://mg.readthedocs.io/git-jupyter.html) is used.

That is, development happens in the `dev` branch, where no cell outputs
are pushed. The latest commit of the master branch is the one with
executed notebooks (that is with `Output[*]` cells). The worflow is then as
follows:
* commit with no `Output` in the dev branch
* rebase the master on dev
* execute the notebooks
* amend the the execute notebook commit on master and force push

Corresponding commands are:
```bash
git checkout dev
# to the changes, run the notebooks
python -m nbconvert --ClearOutputPreprocessor.enabled=True --inplace *.ipynb retrieve_clean_data.ipynb
git add -u
git commit -m "<description>"
git checkout master
git rebase -X ours dev
python -m nbconvert --execute --inplace --ExecutePreprocessor.timeout=600 analysis.ipynb retrieve_clean_data.ipynb
git add -u
git commit --amend --reset-author
git push --force
```
