from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'jose'
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

items = []

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help= "This field cannot be left empty!"
    )

    @jwt_required()
    def get(self, name):
        # for item in items:
        #     if item['name'] == name:
        #         return item
        # return {'item': None}, 404
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item':item}, 200 if item else 404
        
    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': 'item {} already exist'.format(name)}, 400
        
        data = Item.parser.parse_args() #dont need to write contenttype header  (silent=true) will display null insteadof error
        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item, 201

    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'item deleted'}
        
    def put(self, name):
        data = Item.parser.parse_args()
        item = next(filter(lambda x: x['name'] == name, items), None)
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        else:
            item.update(data)
        return item


class ItemList(Resource):
    def get(self):
        return {'items':items}


api.add_resource(Item, '/item/<string:name>') #endpoints
api.add_resource(ItemList, '/items') #endpoints

app.run(port=5000, debug=True)
