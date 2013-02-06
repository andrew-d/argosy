({
    appDir: './src-js',
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
        'respond'      : '../vendor/respond.src',

        // Backbone.Marionette stuff.
        'marionette'            : '../vendor/backbone.marionette',
        'backbone.babysitter'   : '../vendor/backbone.babysitter',
        'backbone.wreqr'        : '../vendor/backbone.wreqr',

        // This depends on all vendor libraries
        'vendor'        : 'vendor',

        // Application code.
        'argosy'        : 'main',
    },
    modules: [
        {
            name: 'vendor',
            include: ['vendor'],
        },
        {
            name: 'argosy',
            exclude: ['vendor'],
        },
    ],
    shim: {
        'underscore': {
            exports: '_'
        },
        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        'marionette' : {
            exports : 'Backbone.Marionette',
            deps : ['backbone']
        }
    },

    // Disable CSS optimization
    optimizeCss: 'none',
    optimize: 'none',
})
