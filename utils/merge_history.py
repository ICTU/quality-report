"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pathlib
import json
import sys


def load_history(filename):
    """ Load the JSON from the history file. """
    path = pathlib.Path(filename)
    with path.open() as history_file:
        return json.loads(history_file.read())


def merge(filename, filename_to_merge):
    """ Merge the second history file (with the newer history) into the first history file. """
    history = load_history(filename)
    to_merge = load_history(filename_to_merge)

    assert len(to_merge["dates"]) == len(to_merge["statuses"])
    # Merge meeasurement time stamps and statuses
    for date, status in zip(to_merge["dates"], to_merge["statuses"]):
        assert date > history["dates"][-1] 
        history["dates"].append(date)
        history["statuses"].append(status)
    # Merge measurements per metric
    for metric in to_merge["metrics"]:
        if metric not in history["metrics"].keys():
            history["metrics"][metric] = []  # Add new metric
        history["metrics"][metric].extend(to_merge["metrics"][metric])

    print(json.dumps(history, sort_keys=True, indent=2))


if __name__ == '__main__':
    merge(sys.argv[1], sys.argv[2])
