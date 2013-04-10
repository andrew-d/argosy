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
        dest: 'build/vendor.js'
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
        dest: 'build/vendor.min.js',
      },
    },

    // Compile and concatenate our coffeescript files.
    coffee: {
      app: {
        options: {
          joined: true
        },
        files: {
          'build/<%= pkg.name %>.js': ['src/**/*.coffee']
        },
      },

      test: {
        options: {
          joined: true,
        },
        files: {
          'build/tests.js': ['test/spec/*.coffee'],
        },
      },

      test_helpers: {
        options: {
          joined: true,
        },
        files: {
          'build/test_helpers.js': ['test/helpers/*.coffee'],
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
        src: 'build/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js',
      },
    },

    // Cleanup
    clean: {
      app: {
        src: ['build/<%= pkg.name %>.js', 'build/<%= pkg.name %>.*.js'],
      },
      vendor: {
        src: ['build/vendor.js'],
      },
    },

    // Coffeescript linting
    coffeelint: {
      app: ['src/**/*.coffee'],
    },

    // Jasmine testing
    jasmine: {
      app: {
        src: ['build/<%= pkg.name %>.js'],
        options: {
          vendor: ['build/vendor.js'],
          specs: ['build/test.js'],
          helpers: ['build/test_helpers.js'],
        },
      },
    },

    // Watch and test.
    // General idea:
    //      - When we modify any of coffeelint's files, re-lint
    //      - When we modify any coffeescript files in src/, build our app
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
        files: ['src/**/*.coffee'],
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
          'build/<%= pkg.name %>.js',
          'build/test.js',
          'build/test_helpers.js',
          'build/vendor.js',
        ],
        tasks: ['jasmine'],
      },
    },

    cache_bust: {
      test: {
        src: 'public/bindex.html',
        dest: 'public/bindex.built.html',
        length: 10,
      },
    }
  });

  // Load the plugin that provides our tasks.
  grunt.loadNpmTasks('grunt-coffeelint');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-jasmine');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Register cache-busting task.  This task will run each source file through
  // underscore.js's template function, with the following function defined:
  //    cbust(file_path)
  // This function, when called, will take the given file, copy it to a new,
  // unique path in the same directory, and then output the given file name in
  // the template.
  grunt.registerMultiTask('cache_bust', 'custom cache-busting logic', function() {
    var data = this.data;

    // Require libraries.
    var path = require('path');
    var crypto = require('crypto');
    var fs = require('fs');

    var cbust = function(file_path) {
      // The file name will be relative to the input file.
      var real_path = path.normalize(path.join(path.dirname(data.src),
                                               file_path
                                               ));

      // Split the file name.
      var name_components = path.basename(file_path).split('.');

      // Hash the file.
      var hash = crypto.createHash('sha256').update(grunt.file.read(real_path));
      var hex = hash.digest('hex');

      // Got the hash.  Get the first 8 characters, add it as a new file
      // name segment, right before the extension.
      var component_len = data.length || 8;
      name_components.splice(name_components.length - 1, 0, hex.slice(0, component_len));

      // Make a new file path.
      var new_name = name_components.join('.');
      var new_real_path = path.join(path.dirname(real_path), new_name);
      var new_rel_path = path.join(path.dirname(file_path), new_name);

      // console.log('New real path: ' + new_real_path);
      // console.log('New relative path: ' + new_rel_path);

      // Copy the input file to the output.
      grunt.file.copy(real_path, new_real_path);

      // Return the new relative path.
      return new_rel_path;
    };

    // Read the source.
    var file_contents = grunt.file.read(data.src);

    // Template it!
    var new_contents = grunt.util._.template(file_contents, {cbust: cbust});

    // Write the new contents to the destination.
    grunt.file.write(data.dest, new_contents);
  });

  // Register tasks
  grunt.registerTask('default', ['concat', 'coffee', 'uglify']);
  grunt.registerTask('test', ['coffeelint', 'jasmine']);
};
