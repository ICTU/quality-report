const webpack = require('webpack'); // to access built-in plugins
const path = require('path');

module.exports = {
  entry: './js/dashboard.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, '../hqlib/app/dist'),
    publicPath: 'dist/'
  },
  plugins: [
    new webpack.ProvidePlugin({
      jQuery: 'jquery',
      $: 'jquery',
      jquery: 'jquery'
    }),
    new webpack.optimize.UglifyJsPlugin()
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        use: 'babel-loader'
      },
      {
        test: /\.css$/,
        use: [ 'style-loader', 'css-loader' ]
      },
      {
		test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
		use: [{
          loader: 'file-loader',
          options: {
            limit: 10000,
            mimetype: 'application/font-woff'
          }
        }]
      },
      {
        test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            limit: 10000,
            mimetype: 'application/font-woff2'
          }
        }]
      },
      {
        test: /\.[ot]tf(\?v=\d+\.\d+\.\d+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            limit: 10000,
            mimetype: 'application/octet-stream'
          }
        }]
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: "file-loader"
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            limit: 10000,
            mimetype: 'image/svg+xml'
          }
        }]
	  }
    ]
  }
};
