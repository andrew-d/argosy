define([ "jquery", "underscore", "backbone", "modernizr", "handlebars" ],
function( jQuery,        _,            Backbone,   Modernizr,   Handlebars ) {
    jQuery.noConflict();
    _.noConflict();
    Backbone.noConflict();
    Modernizr = (!Modernizr) ? window.Modernizr : 'undefined';

    // Just return the libraries as-is.
    return {
        'jQuery'     : jQuery,
        '$'          : jQuery,
        '_'          : _,
        'Backbone'   : Backbone,
        'Modernizr'  : Modernizr,
        'Handlebars' : Handlebars,
    }
});
