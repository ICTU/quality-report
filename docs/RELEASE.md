1. Update change history in `docs/CHANGES.md`
1. Update version numbers in `hqlib/__init__.py`, `hqlib/app/package.json` and  `sonar-project.properties`
1. Create the bundle by running the integration tests
1. Create source distribution and upload it to the Python Package Index: 
   `python setup.py sdist upload`
1. Create Docker image and push to Docker Hub: 
   `docker build --no-cache -t ictu/quality-report .; docker push ictu/quality-report`
