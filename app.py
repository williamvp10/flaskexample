from flask import Flask, jsonify, request
from flask_restful import Resource, reqparse, Api
from rasa_nlu.training_data import load_data
from rasa_nlu.model import Interpreter

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

from base import Movies, db
db.init_app(app)
app.app_context().push()
db.create_all()

class Movies_List(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('director', type=str, required=False, help='Director of the movie')
    parser.add_argument('genre', type=str, required=False, help='Genre of the movie')
    parser.add_argument('collection', type=int, required=True, help='Gross collection of the movie')
    
    def get(self, movie):
        item = Movies.find_by_title(movie)
        if item:
            return item.json()
        return {'Message': 'Movie is not found'}
    
    def post(self, movie):
        if Movies.find_by_title(movie):
            return {' Message': 'Movie with the  title {} already exists'.format(movie)}
        args = Movies_List.parser.parse_args()
        item = Movies(movie, args['director'], args['genre'], args['collection'])
        item.save_to()
        return item.json()
        
    def put(self, movie):
        args = Movies_List.parser.parse_args()
        item = Movies.find_by_title(movie)
        if item:
            item.collection = args['collection']
            item.save_to()
            return {'Movie': item.json()}
        item = Movies(movie, args['director'], args['genre'], args['collection'])
        item.save_to()
        return item.json()
            
    def delete(self, movie):
        item  = Movies.find_by_title(movie)
        if item:
            item.delete_()
            return {'Message': '{} has been deleted from records'.format(movie)}
        return {'Message': '{} is already not on the list'.format()}
    
class All_Movies(Resource):
    def get(self):
        return {'Movies': list(map(lambda x: x.json(), Movies.query.all()))}
    
    
    
class index(Resource):
    def get(self):
        return "<p> Horoscope bot <p>"


class intent(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        text = json_data['text']
        json= predict_intent(text)
        return json

    
def predict_intent(text):
    interpreter = Interpreter.load('./models/nlu/default/horoscopebot')
    return interpreter.parse(text)



api.add_resource(intent, '/intent')
api.add_resource(All_Movies, '/')
api.add_resource(Movies_List, '/<string:movie>')

if __name__=='__main__':
    
    app.run(debug=True)
