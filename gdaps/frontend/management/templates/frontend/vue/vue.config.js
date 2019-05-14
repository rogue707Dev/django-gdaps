const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    // The base URL your application bundle will be deployed at
    publicPath: 'http://localhost:8080/',
    // The directory where the production build files will be generated in when running vue build.
    // This must be Django's assets directory
    outputDir: './dist/',
    // enable single file Vue components
    runtimeCompiler: true,

    chainWebpack: config => {

        config.optimization
            .splitChunks(false)

        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{
                // filename: 'webpack-stats.json' // = default
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
                // Forward frontend dev server request for /admin to django dev server
                '/admin*': {
                    target: 'http://localhost:8000/',
                }
             })
    }
};
