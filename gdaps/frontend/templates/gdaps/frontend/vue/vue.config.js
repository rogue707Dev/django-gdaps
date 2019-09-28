const BundleTracker = require("webpack-bundle-tracker");
const gdaps_plugins = require('./plugins.js');

module.exports = {
    // The base URL your application bundle will be deployed at
    publicPath: 'http://localhost:8080/',
    // The directory where the production build files will be generated in when running vue build.
    // This must be Django's assets directory
    outputDir: './dist/',
    // enable single file Vue components
    runtimeCompiler: true,

    // First, use a merge object, because webpack-chain doesn't support
    // dynamic webpack entry points (yet).
    // see https://github.com/neutrinojs/webpack-chain/issues/200
    configureWebpack: {
      entry: () => {
        return gdaps_plugins
      }
    },
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
                "Access-Control-Allow-Origin": ["*"]
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