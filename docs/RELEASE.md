1. Update change history in `docs/CHANGES.md`
1. Update version numbers in `python/qualitylib/__init__.py` and  `sonar-project.properties`
1. Create source distribution and upload it to the Python Package Index: 
   `cd python; python setup.py sdist upload; cd ..`
1. Create Docker image and push to Docker Hub: 
   `docker build --no-cache -t ictu/quality-report .; docker push ictu/quality-report`
