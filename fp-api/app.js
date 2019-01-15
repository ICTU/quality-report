var express = require("express");
var bodyParser = require('body-parser');
var cors = require('cors');

var app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());

require('./app/routes/fp.routes.js')(app);

app.listen(3000, () => {
	console.log("Server running on port 3000");
});
