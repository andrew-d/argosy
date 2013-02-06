source 'http://rubygems.org'

group :test, :development do
  gem 'guard'

  gem 'guard-bundler'
  gem 'guard-coffeescript'
  gem 'guard-livereload'
  gem 'guard-process'
  gem 'guard-shell'

  gem 'rb-inotify', :require => false
  gem 'rb-fsevent', :require => false
  gem 'wdm', :platforms => [:mswin, :mingw], :require => false

  gem 'rb-readline'

  # Make color work on Windows.
  gem 'win32console', :platforms => [:mswin, :mingw]

  # Terminal notifier for OS X.  I'm not a huge fan of this, since Gemfile.lock
  # is no longer constant across platforms, but cross-platform consistency is
  # probably worth it.
  if RUBY_PLATFORM =~ /darwin/
    gem 'terminal-notifier-guard'
  end
end
