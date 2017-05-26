const webpack = require('webpack'); // to access built-in plugins
const path = require('path');

module.exports = {
  entry: './js/dashboard.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    publicPath: 'dist'
  },
  plugins: [
    new webpack.ProvidePlugin({   
      jQuery: 'jquery',
      $: 'jquery',
      jquery: 'jquery'
    })
  ]
};

