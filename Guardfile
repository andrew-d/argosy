require 'fileutils'

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

def build_with_requirejs
  colored(34) do              # blue!
    Dir.chdir('frontend') do
      system 'r.js -o app.build.js'
    end
  end
end

group :frontend do
  guard :coffeescript, :bare => true, :output => 'frontend/src-js/' do
    watch(%r{^frontend/src/(.+\.coffee)$})
  end

  guard :shell do
    watch(%r{^frontend/src-js/(.+)$}) {|m| build_with_requirejs }
    watch(%r{^frontend/app\.build\.js$}) {|m| build_with_requirejs }

    watch(%r{^frontend/public/(.+)$}) do |m|
      colored(34) do
        puts 'Copying public to build dir...'
        FileUtils::cp_r('frontend/public/.', 'frontend/build')
      end
    end

    watch(%r{^frontend/build-js/(.+)$}) do |m|
      colored(34) do
        puts 'Copying JS to build dir'
        FileUtils::mkdir_p('frontend/build/')
        FileUtils::cp('frontend/build-js/app.js', 'frontend/build/js/')
        FileUtils::cp('frontend/build-js/vendor.js', 'frontend/build/js/')
      end
    end
  end

  guard :livereload do
    watch(%r{frontend/build/.+\.(css|js|html)})
  end
end
