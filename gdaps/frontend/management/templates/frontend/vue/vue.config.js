const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    publicPath: 'http://localhost:8080/'
    outputDir: './dist/',

    chainWebpack: config => {

        config.optimization
            .splitChunks(false)

        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{
                filename: '../{{ frontend_dir }}/webpack-stats.json'
            }])

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://localhost:8080')
            .host('localhost')
            .port(8080)
            .hotOnly(true)
            .watchOptions({
                poll: 1000
            })
            .https(false)
            .headers({
                "Access-Control-Allow-Origin": ["\*"]
            })
            .proxy({
                // Forward frontend dev server request for /api to django dev server
                '/api*': {
                    target: 'http://localhost:8000/',
                },
                '/admin*': {
                    // Forward frontend dev server request for /admin to django dev server
                    target: 'http://localhost:8000/',
                }
             })
    }
};
