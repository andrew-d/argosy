dep.define 'main', ['app', 'dom'], ->
  App = window.App

  App.start()
  Backbone.history.start()
