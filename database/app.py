# app.py
from flask import Flask
from endpoints.data.pie_endpoint import pie_bp
from endpoints.data.groupsentimen_endpoint import groupsentimen_bp

app = Flask(__name__)
app.register_blueprint(pie_bp, url_prefix='/api')
app.register_blueprint(groupsentimen_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
