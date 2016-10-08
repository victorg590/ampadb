# Destinació dels arxius
dest_dir = 'out'

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
          src: "*/static/**/*.{sass,scss}"
          dest: dest_dir
          rename: rename
          }]
      coffee:
        files: [{
            expand: true
            src: "*/static/**/*.coffee"
            dest: dest_dir
            rename: rename
          }]
      generic:
        files: [{
          expand: true
          src: ["*/static/**/*", "!*/static/**/*.{sass,scss,coffee}"]
          dest: dest_dir
          rename: rename
          }]
    sass:
      compile:
        options:
          sourcemap: 'auto'
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
        files: ["*/static/**/*", "!*/static/**/*.{sass,scss,coffee}",
          "!**/*~", "!**/*.bck*"]
        tasks: ['copy:generic']
      sass:
        files: "*/static/**/*.{sass,scss}"
        tasks: ['copy:sass', 'sass', 'cssmin']
      coffee:
        files: "*/static/**/*.coffee"
        tasks: ['copy:coffee', 'coffee', 'uglify']
    clean:
      rmDest:
        files: [{
          expand: true
          src: ["#{dest_dir}/**/*", "#{dest_dir}/**", dest_dir]
          }]

  grunt.loadNpmTasks 'grunt-contrib-copy'
  grunt.loadNpmTasks 'grunt-contrib-sass'
  grunt.loadNpmTasks 'grunt-contrib-cssmin'
  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-clean'

  grunt.registerTask 'css', ['sass', 'cssmin']
  grunt.registerTask 'js', ['coffee', 'uglify']
  grunt.registerTask 'default', ['copy', 'css', 'js']
  return
