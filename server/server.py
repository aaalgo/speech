#!/usr/bin/env python3
import os
import json
from collections import defaultdict
from flask import Flask, jsonify, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import *
from schema import AutoSchema
import image
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
db = SQLAlchemy()
db.init_app(app)

schema = AutoSchema()

# ================================ WEB =================================
@app.route('/')
def index ():
    return redirect("/web/", code=302)

@app.route('/web/')
def app_index ():
    return send_file(f'web/build/index.html')

@app.route('/web/<path:filename>')
def app_file (filename): 
    try:
        return send_file(f'web/build/{filename}')
    except FileNotFoundError:
        return send_file(f'web/build/index.html')
    
# ================================ General DB API  ================================

@app.route('/api/db/get/<string:table>/<int:id>/')
def api_db_get (table, id):
    return jsonify(schema.get(db.session, table, id))

@app.route('/api/db/query/<string:table>/')
def api_db_query (table):
    return schema.query(db.session, table, request.args)

# ================================ Deck API  ================================
                    
@app.route('/api/deck/create/', methods=['POST'])
def api_deck_create():
    data = request.json
    deck = Deck(name=data['name'])
    db.session.add(deck)
    db.session.flush()
    # root
    root = Node(deck_id=deck.id)
    db.session.add(root)
    # 1st slide
    node1 = Node(deck_id=deck.id)
    db.session.add(node1)
    db.session.commit()
    deck.save({ # default tree
        'root': {
            'node_id': root.id,
            'label': 'root',
            'children': [
                {
                    'node_id': node1.id,
                    'label': 'node1'
                }
            ]
        }})
    return jsonify({'id':deck.id})

@app.route('/api/deck/load/<int:deck_id>/')
def api_deck_load (deck_id):
    deck = db.session.get(Deck, deck_id)
    return deck.load()

@app.route('/api/deck/save/<int:deck_id>/', methods=['POST'])
def api_deck_save (deck_id):
    data = request.json
    deck = db.session.get(Deck, deck_id)
    deck.save(data)
    return jsonify({'id':deck.id})

# ================================ Node API  ================================

@app.route('/api/node/create/', methods=['POST'])
def api_node_create():
    data = request.json
    node = Node(deck_id=data['deck_id'])
    db.session.add(node)
    db.session.commit()
    return {'id':node.id}

@app.route('/api/node/load/<int:node_id>/')
def api_node_load (node_id):
    node = db.session.get(Node, node_id)
    return node.load()


@app.route('/api/node/save/<int:node_id>/', methods=['POST'])
def api_node_save (node_id):
    data = request.json
    node = db.session.get(Node, node_id)
    node.save(data)
    return {'id':node.id}

#@app.route('/api/node/<int:deck_id>/node/<int:node_id>/script/<int:script_id>/')
#def api_script (deck_id, node_id, script_id):
#    script = db.session.get(Script, script_id)
#    return jsonify(script.to_dict())    



if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True)

