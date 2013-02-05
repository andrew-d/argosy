({
    appDir: './src',
    baseUrl: './',
    dir: './build',
    paths: {
        // 3rd-party vendor libraries
        'json2'        : '../vendor/json2',
        'modernizr'    : '../vendor/modernizr',
        'jquery'       : '../vendor/jquery-1.9.1',
        'underscore'   : '../vendor/lodash',
        'handlebars'   : '../vendor/handlebars',
        'backbone'     : '../vendor/backbone',

        // This depends on all vendor libraries
        'vendor'       : 'vendor',

        // Application code.
        'app'          : 'application',
    },
    modules: [
        {
            name: 'vendor',
            include: ['vendor']
        },
        {
            name: 'app',
            exclude: ['vendor']
        },
    ],
    shim: {
        'underscore': {
            exports: '_'
        },
        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        }
    },

    // Disable CSS optimization
    optimizeCss: 'none',
})
