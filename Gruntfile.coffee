{dest_dir, static_dir} = require './build_conf'
sassimpl = require 'sass'

rename = (dest, src) ->
  split_src = src.split '/'
  if split_src[0] is 'ampadb_index'
    new_src = split_src[2..].join '/'
  else
    new_src = split_src[0] + '/' + split_src[2..].join '/'
  [dest, new_src].join '/'

module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON 'package.json'
    copy:
      sass:
        files: [{
          expand: true
          src: "*/#{static_dir}/**/*.{sass,scss}"
          dest: dest_dir
          rename: rename
        }]
      coffee:
        files: [{
            expand: true
            src: "*/#{static_dir}/**/*.coffee"
            dest: dest_dir
            rename: rename
        }]
      generic:
        files: [{
          expand: true
          src: [
            "*/#{static_dir}/**/*",
            "!*/#{static_dir}/**/*.{sass,scss,coffee}"
          ]
          dest: dest_dir
          rename: rename
        }]
    sass:
      compile:
        options:
          implementation: sassimpl
          sourceMap: true
          includePaths: [dest_dir]
        files: [{
          expand: true
          src: "#{dest_dir}/**/*.{sass,scss}"
          ext: '.css'
        }]
    cssmin:
      minimizeCss:
        files: [{
          expand: true
          src: ["#{dest_dir}/**/*.css", "!#{dest_dir}/**/*.min.css"]
          ext: '.min.css'
        }]
    coffee:
      compile:
        options:
          sourceMap: true
        files: [{
          expand: true
          src: "#{dest_dir}/**/*.coffee"
          ext: '.js'
        }]
    uglify:
      minimizeJs:
        files: [{
          expand: true
          src: ["#{dest_dir}/**/*.js", "!#{dest_dir}/**/*.min.js"]
          ext: '.min.js'
        }]

    watch:
      generic:
        files: [
          "*/#{static_dir}/**/*"
          "!*/#{static_dir}/**/*.{sass,scss,coffee}"
          "!**/*~"
          "!**/*.bck*"
        ]
        tasks: ['copy:generic']
      sass:
        files: "*/#{static_dir}/**/*.{sass,scss}"
        tasks: ['copy:sass', 'sass', 'cssmin']
      coffee:
        files: "*/#{static_dir}/**/*.coffee"
        tasks: ['copy:coffee', 'coffee', 'uglify']
    coffeelint:
      coffee: "*/#{static_dir}/**/*.coffee"
    sasslint:
      options:
        configFile: ".sass-lint.yml"
      sass: "*/#{static_dir}/**/*.{sass,scss}"
    clean:
      rmDest:
        files: [{
          expand: true
          src: ["#{dest_dir}/**/*", "#{dest_dir}/**", dest_dir]
        }]

  grunt.loadNpmTasks 'grunt-contrib-copy'
  grunt.loadNpmTasks 'grunt-sass'
  grunt.loadNpmTasks 'grunt-contrib-cssmin'
  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-coffeelint'
  grunt.loadNpmTasks 'grunt-sass-lint'
  grunt.loadNpmTasks 'grunt-contrib-clean'

  grunt.registerTask 'css', ['copy:sass', 'sass', 'cssmin']
  grunt.registerTask 'js', ['copy:coffee', 'coffee', 'uglify']
  grunt.registerTask 'test', ['coffeelint', 'sasslint']
  grunt.registerTask 'all', ['copy', 'css', 'js']
  grunt.registerTask 'default', 'all'
  return
