module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Concatenate vendor libraries together.
    concat: {
      vendor: {
        // Note: Order is important, since these aren't using AMD builds.
        src: [
          'vendor/debug/json2.js',
          'vendor/debug/jquery-1.9.1.js',
          'vendor/debug/modernizr.js',
          'vendor/debug/lodash.compat.js',
          'vendor/debug/backbone.js',
          'vendor/debug/backbone.marionette.js',    // NOTE: this bundled build
                                                    // also includes babysitter
                                                    // and wreqr.
          'vendor/debug/handlebars.js',
          'vendor/debug/respond.src.js',
          'vendor/debug/dep.js',
        ],
        dest: 'build/js/vendor.js'
      },

      // This task concatenates vendor pre-minified libraries.  The reason we
      // use this rather than do it ourselves is because I don't want to have
      // to remember what settings each library can be minified with - and
      // also, an individual library's developers will presumably know what
      // minification options achieve the best compression.
      vendor_min: {
        // Note: order is the same as above.
        src: [
          'vendor/min/json2.min.js',                // Manually minified.
          'vendor/min/jquery-1.9.1.min.js',
          'vendor/min/modernizr.min.js',
          'vendor/min/lodash.compat.min.js',
          'vendor/min/backbone-min.js',
          'vendor/min/backbone.marionette.min.js',  // NOTE: this bundled build
                                                    // also includes babysitter
                                                    // and wreqr.
          'vendor/min/handlebars.min.js',           // Manually minified.
          'vendor/min/respond.min.js',
          'vendor/debug/dep.min.js',
        ],
        dest: 'build/js/vendor.min.js',
      },
    },

    // Compile and concatenate our coffeescript files.
    coffee: {
      app: {
        options: {
          joined: true
        },
        files: {
          'build/js/<%= pkg.name %>.js': ['coffee/**/*.coffee']
        },
      },

      test: {
        options: {
          joined: true,
        },
        files: {
          'build/js/tests.js': ['test/spec/*.coffee'],
        },
      },

      test_helpers: {
        options: {
          joined: true,
        },
        files: {
          'build/js/test_helpers.js': ['test/helpers/*.coffee'],
        },
      },
    },

    // Minify the built coffeescript files.
    uglify: {
      options: {
        report: 'min',
      },
      app: {
        options: {
          banner: '/*! <%= pkg.name %>, built: <%= grunt.template.today("yyyy-mm-dd") %> */\n'
        },
        src: 'build/js/<%= pkg.name %>.js',
        dest: 'build/js/<%= pkg.name %>.min.js',
      },
    },

    // Compile SASS to CSS.
    sass: {
      main: {
        // bundleExec: true,
        files: {
          'build/css/main.css': [
            'scss/main.scss',
          ],
        },
      },
    },

    // Copy some files to the build directory.
    copy: {
      favicon: {
        files: [
          {src: 'favicon.ico', dest: 'build/favicon.ico'},
        ],
      },
      index: {
        files: [
          {src: 'index.html', dest: 'build/index.html'},
        ],
      },
    },

    // Process the index file to cache-bust.
    cache_bust: {
      app: {
        src: 'build/index.html',
        dest: 'build/index.html',
        length: 10,
        method: 'filename',                     // Valid: 'filename' (default),
                                                //         'querystring'
      },
    },

    // Cleanup
    clean: {
      app: {
        src: ['build/js/<%= pkg.name %>.js', 'build/js/<%= pkg.name %>.*.js'],
      },
      vendor: {
        src: ['build/js/vendor.js', 'build/js/vendor.min.js'],
      },
      favicon: {
        src: ['build/favicon.ico'],
      },
      css: {
        src: ['build/css/*.css'],
      },
    },

    // Coffeescript linting
    coffeelint: {
      app: ['coffee/**/*.coffee'],
    },

    // Jasmine testing
    jasmine: {
      app: {
        src: ['build/js/<%= pkg.name %>.js'],
        options: {
          vendor: ['build/js/vendor.js'],
          specs: ['build/js/test.js'],
          helpers: ['build/js/test_helpers.js'],
        },
      },
    },

    // Watch and test.
    // General idea:
    //      - When we modify any of coffeelint's files, re-lint
    //      - When we modify any coffeescript files in coffee/, build our app
    //      - When we modify any test files, rebuild the test JS files
    //      - When any JS files in the vendor directory are changed, rebuild
    //        the appropriate concatenated or regular file.
    //      - When any built JS files have been changed, re-test
    watch: {
      // lint: {
      //   files: ['Gruntfile.js', '<%= coffeelint.files %>'],
      //   tasks: ['coffeelint']
      // },
      build: {
        files: ['coffee/**/*.coffee'],
        tasks: ['coffee:app'],
      },
      build_test: {
        files: ['test/spec/*.coffee', 'test/helpers/*.coffee',],
        tasks: ['coffee:test', 'coffee:test_helpers'],
      },
      vendor: {
        files: ['vendor/debug/*.js'],
        tasks: ['concat:vendor'],
      },
      vendor_min: {
        files: ['vendor/min/*.js'],
        tasks: ['concat:vendor_min'],
      },
      test: {
        files: [
          'Gruntfile.js',
          'build/js/<%= pkg.name %>.js',
          'build/js/test.js',
          'build/js/test_helpers.js',
          'build/js/vendor.js',
        ],
        tasks: ['jasmine'],
      },
    },
  });

  // Load the plugin that provides our tasks.
  grunt.loadNpmTasks('grunt-coffeelint');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-jasmine');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Register cache-busting task.  This task will run each source file through
  // underscore.js's template function, with the following function defined:
  //    cbust(url)
  // This function, when called, will take the file at the given url, copy it
  // to a new, unique path in the same directory, and then output the given
  // file name in the template.
  grunt.registerMultiTask('cache_bust', 'custom cache-busting logic', function() {
    var data = this.data;

    // Require libraries.
    var path = require('path');
    var crypto = require('crypto');
    var fs = require('fs');
    var url = require('url');
    var _ = grunt.util._;

    var cbust = function(resource_url) {
      // The input value is a resource URL relative to the input file.  We
      // parse the URL, and then get the file path from that.
      var urlObj = url.parse(resource_url, true);

      // The real path to this item on-disk is the relative path from
      // the directory of the source file to the path name.
      var real_path = path.normalize(path.join(path.dirname(data.src),
                                               urlObj.pathname
                                               ));

      // Hash the file.
      var hash = crypto.createHash('sha256').update(grunt.file.read(real_path));

      // Got the hash.  Extract the specified number of characters (default: 8).
      var cache_str = hash.digest('hex').slice(0, data.length || 8);

      if( cache_str.length <= 2 ) {
        grunt.log.write("NOTE: It is not recommended to use cache-busting " +
                        "strings of length 2 or lower.");
      }

      var return_path;
      var method = data.method || 'filename';
      if( 'filename' === method ) {
        // Split the URL, and place the cache string as a new component
        // just before the extension.
        var name_components = _.last(urlObj.pathname.split('/')).split('.');
        name_components.splice(name_components.length - 1, 0,
                               cache_str
                               );

        var new_name = name_components.join('.');

        // We copy to the new path name.
        var dest_path = path.join(path.dirname(real_path), new_name);
        // console.log('Destination path: ' + dest_path);
        grunt.file.copy(real_path, dest_path);

        return_path = _.initial(urlObj.pathname.split('/')).concat(new_name).join('/');
      } else if( 'querystring' === method ) {
        // Remove any existing "search" entry.
        urlObj.search = null;

        // Add new querystring entry of our cache string.
        urlObj.query[cache_str] = '1';
        return_path = url.format(urlObj);
      }

      // console.log('Return path: ' + return_path);

      // Return the new relative path.
      return return_path;
    };

    // Read the source that we're given.
    var file_contents = grunt.file.read(data.src);

    // Allow the user to override template variables, or settings.
    var settings = data.settings || {};
    var templ_data = {};
    if( data.vars ) {
        var vars = data.vars;
        if( typeof vars === 'function' ) {
            vars = vars();
        }
        _.extend(templ_data, vars);
    }
    _.extend(templ_data, {cbust: cbust});

    var new_contents = _.template(file_contents, {cbust: cbust}, settings);

    // Write the new contents to the destination.
    grunt.file.write(data.dest, new_contents);
  });

  // Register tasks
  grunt.registerTask('default', ['concat', 'coffee', 'uglify', 'sass', 'copy', 'cache_bust']);
  grunt.registerTask('test', ['coffeelint', 'jasmine']);
};
