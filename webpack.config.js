const path = require('path');

module.exports = {
    mode: 'production',
    entry: './frontend/app.ts',
    output: {
        filename: 'app.js',
        path: path.resolve(__dirname, 'frontend'),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    devtool: 'source-map',
};
