var fs = require('fs');

var falsepositives = {}
var datafile = 'data/data.json';

loadData = function () {
    fs.readFile(datafile, 'utf8', function readFileCallback(err, data) {
        if (err) {
            console.log(err);
        } else {
            if(data === '') {
                data = '{}';
            }
            falsepositives = JSON.parse(data);
        }
    });
}

writeData = function () {
    var json = JSON.stringify(falsepositives);
    fs.writeFile(datafile, json, 'utf8', function writeFileCallback(err, data) {
		if (err) {
            console.log(err);
        } else {
			loadData();
		}
	});
}

loadData();

exports.findAll = function (req, res) {
    var fps = JSON.stringify(falsepositives, null, 4);
    
    res.end(fps);
};

exports.findOne = function (req, res) {
    console.log("findOne: \n" + req.params.id);
	
    var fp = falsepositives[req.params.id];

    console.log("findOne result: \n" + JSON.stringify(fp, null, 4));

    res.end(JSON.stringify(fp, null, 4));
};

exports.updateOrCreate = function (req, res) {
    var postedFP = req.body;

    console.log("updateOrCreate: \n" + req.params.id + "\n" + JSON.stringify(postedFP, null, 4));

    falsepositives[req.params.id] = postedFP;

    writeData();

    res.end(JSON.stringify(postedFP, null, 4));
};

exports.delete = function (req, res) {
    console.log("delete: \n" + req.params.id);

	delete falsepositives[req.params.id];
	
    writeData();

    res.end("deleted: \n" + req.params.id);
};