module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Concatenate vendor libraries together.
    concat: {
      vendor: {
        src: [
          'vendor/json2.js',
          'vendor/jquery-1.9.1.js',
          'vendor/modernizr.js',
          'vendor/lodash.js',
          'vendor/backbone.js',
          'vendor/backbone.babysitter.js',
          'vendor/backbone.wreqr.js',
          'vendor/backbone.marionette.js',
          'vendor/handlebars.js',
          'vendor/respond.src.js',
        ],
        dest: 'build/vendor.js'
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
      app: {
        options: {
          banner: '/*! <%= pkg.name %>, built: <%= grunt.template.today("yyyy-mm-dd") %> */\n'
        },
        src: 'build/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js',
      },
      vendor: {
        src: 'build/vendor.js',
        dest: 'build/vendor.min.js',
      }
    },

    // Cleanup
    clean: {
      app: {
        src: ['build/<%= pkg.name %>.js', 'build/<%= pkg.name %>.min.js'],
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
    //        the concatenated vendor file
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
        files: ['vendor/*.js'],
        tasks: ['concat:vendor'],
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
    }
  });

  // Load the plugin that provides our tasks.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-jasmine');
  grunt.loadNpmTasks('grunt-coffeelint');

  // Register tasks
  grunt.registerTask('default', ['concat', 'coffee', 'uglify']);
  grunt.registerTask('test', ['coffeelint']);
};



