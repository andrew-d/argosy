from backend.api import app, db

# db.create_all() will only work if there is a request context
with app.test_request_context():
    db.create_all()

app.run(debug=True)
