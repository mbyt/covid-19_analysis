# Covid-19 Analysis

In order to avoid polluting the `git diff` through changed `Output[*]`
cells (especially images are problematic), the development workflow
as described in https://mg.readthedocs.io/git-jupyter.html is used:

That is, development happens in the `dev` branch, where no cell outputs
are pushed. The latest commit of the master branch is the one with
executed notebooks (that is with `Output[*]` cells). The worflow is then as
follows:
* commit with no `Output` in the dev branch
* rebase the master on dev
* execute the notebooks
* ammend the the execute notebook commit on master and force push

The corresponding commands for the master branch are:
```bash
git checkout dev
# to the changes, run the notebooks
python -m nbconvert --ClearOutputPreprocessor.enabled=True --inplace analysis.ipynb retrieve_clean_data.ipynb
git commit -m "<description>"
git checkout master
git rebase -X ours dev
python -m nbconvert --execute --inplace --ExecutePreprocessor.timeout=600 analysis.ipynb retrieve_clean_data.ipynb
git commit --amend --reset-author
git push --force
```
