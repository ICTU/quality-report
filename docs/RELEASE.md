To create source distribution and upload it to the Python Package Index:

* `cd python`
* `python setup.py sdist upload`

To create Docker image and push to Docker Hub:

* `docker build --no-cache -t ictu/quality-report .`
* `docker push ictu/quality-report`
