require 'pathname'

desc 'compiles coffeescript to javascript'
task :coffee do
  src_dir = Pathname.new('frontend/src')

  Dir.glob('frontend/src/**/*.coffee') do |f|
    puts "Compiling: #{f.inspect}"

    # We want the path of the file, with the same directory structure, relative
    # to the src-js directory.  We do this in a couple of steps:
    #   1. Get the filename by itself.
    fname = Pathname.new(f).basename

    #   2. Get the directory name of the file, relative to the source directory
    dname = Pathname.new(f).dirname.relative_path_from(src_dir)

    #   3. Prepend the src-js directory to it to get the new directory path.
    new_dir = Pathname.new('frontend/src-js') + dname

    #   4. Get the filename of the new JS file in this directory.
    js_file = new_dir + fname.sub_ext('.js')

    # Make the directory, then compile to the file.
    mkdir_p new_dir.to_s
    sh "coffee --bare --compile --print #{f} > #{js_file.to_s}"
  end
end

desc 'build javascript with requirejs optimizer'
task :build_js => [:coffee] do
  # Run the optimizer in the correct directory.
  Dir.chdir('frontend') do
    sh 'r.js -o app.build.js'
  end
end
