1. Update change history in `docs/CHANGES.md`
1. Update version numbers in `backend/hqlib/__init__.py`, `frontend/package.json` and  `sonar-project.properties`
1. Commit.
1. Add a tag of the form `v<major>.<minor>.<patch>`.
1. Push (`git push --tags`). This will trigger a Travis release build which will create and upload a new Python package to 
   the Python Package Index (PyPI) and will create and upload a Docker image to Docker Hub.
