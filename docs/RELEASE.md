1. Update change history in `docs/CHANGES.md`
1. Update version numbers in `hqlib/__init__.py`, `frontend/package.json` and  `sonar-project.properties`
1. Add a tag of the form `v<major>.<minor>.<patch>`
1. Commit and push. This will trigger a Travis release build which will create and upload a new Python package to PyPI.
1. Run `release.sh` locally to create and upload the Docker image.
