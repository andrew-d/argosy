# Simple color helper.
def colored(code, &block)
  puts "\033[#{code.to_s}m"
  yield
ensure
  puts "\033[0m"
end


group :backend do
  # Run bundler generating binstubs (because of rbenv)
  guard :bundler, :cli => '--binstubs' do
    watch('Gemfile')
  end
end

group :frontend do
  guard :coffeescript, :bare => true, :output => 'frontend/src-js/' do
    watch(%r{^frontend/src/(.+\.coffee)$})
  end

  guard :shell do
    watch(%r{^frontend/src-js/(.+)$}) do |m|
      colored(34) do              # blue!
        Dir.chdir('frontend') do
          system 'r.js -o app.build.js'
        end

        # Write our proper .gitignore, since it keeps getting clobbered.
        File.open('frontend/build/.gitignore', 'w') do |f|
          f.write <<-EOG
# This directory is used for compiled CoffeeScript, and thus should be ignored.
*.js
*.txt
EOG
        end
      end
    end
  end

  guard :livereload do
    watch(%r{frontend/build/.+\.(css|js|html)})
  end
end
