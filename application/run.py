from application.app import create_app,db

flask_app = create_app()

if __name__== '__main__':
    flask_app.run('0.0.0.0',port=5000, debug=True)
