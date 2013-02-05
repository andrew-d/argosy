# Simple color helper.
def colored(code, &block)
  puts "\033[#{code.to_s}m"
  yield
ensure
  puts "\033[0m"
end


group :backend do
  guard :bundler, :cli => '--binstubs' do
    watch('Gemfile')
  end
end

group :frontend do
  guard :coffeescript, :output => 'frontend/src-js/' do
    watch(%r{^frontend/src/(.+\.coffee)$})
  end

  guard :shell do
    watch(%r{^frontend/src-js/(.+)$}) do |m|
      Dir.chdir('frontend') do
        colored(34) do              # blue!
          system 'r.js -o app.build.js'
        end
      end
    end
  end
end
