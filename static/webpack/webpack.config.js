const path = require('path');

module.exports = {
    entry: {
        main: './src/main.js'
    },
    mode: 'production',
    devtool: 'eval-source-map',
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, '../js'),
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
        ],
    },
    watch: true,
};