var fp = require('../controllers/fp.controller.js');

module.exports = function(app) { 
    // Retrieve all FP's
    app.get('/api/fp', fp.findAll);
 
    // Retrieve a single FP by Id
    app.get('/api/fp/:id', fp.findOne);
 
    // Update a FP
    app.post('/api/fp/:id', fp.updateOrCreate);
 
    // Delete a FP with Id
    app.delete('/api/fp/:id', fp.delete);
}
