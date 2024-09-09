#!/usr/bin/env python3
import os
import json
import subprocess as sp
import pickle
from collections import defaultdict
from flask import Flask, jsonify, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import *
from schema import AutoSchema
import image
from llm import GPT
from gen_slide import gen_slide
from gen_script import gen_script
from gen_menuscript import gen_menuscript
from gen_audio import gen_audio
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
    return send_file(f'../web/build/index.html')

@app.route('/web/<path:filename>')
def app_file (filename): 
    try:
        return send_file(f'../web/build/{filename}')
    except FileNotFoundError:
        return send_file(f'../web/build/index.html')
    
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

def update_meta_tree(deck_id, node):
    node_id = node['node_id']
    node['thumb'] = Node.base64_thumb(deck_id, node_id)
    if not 'children' in node:
        return
    for child in node['children']:
        update_meta_tree(deck_id, child)

@app.route('/api/deck/load/<int:deck_id>/')
def api_deck_load (deck_id):
    deck = db.session.get(Deck, deck_id)
    data = deck.load()
    if 'root' in data:
        update_meta_tree(deck_id, data['root'])
    data['blank_thumb'] = image.base64_encode(image.empty())
    return data;

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

def save_node(node_id, data):
    node = db.session.get(Node, node_id)
    node.content.save(data)
    return node

@app.route('/api/node/save/<int:node_id>/', methods=['POST'])
def api_node_save (node_id):
    node = save_node(node_id, request.json)
    return {'id':node.id}

@app.route('/api/node/generate_slide/<int:node_id>/', methods=['POST'])
def api_node_generate_slide (node_id):
    node = save_node(node_id, request.json)
    # update slide data
    node.slide.save({})  # create new snapshot
    return gen_slide(node.content.current('data.json'), node.slide.current())


@app.route('/api/node/generate_script/<int:node_id>/', methods=['POST'])
def api_node_generate_script (node_id):
    node = save_node(node_id, request.json)
    node.script.save({})  # create new snapshot
    return gen_script(node.content.current('data.json'), node.script.current())

@app.route('/api/node/generate_menuscript/<int:node_id>/', methods=['POST'])
def api_node_generate_menuscript(node_id):
    node = save_node(node_id, request.json)
    node.menuscript.save({})  # create new snapshot
    return gen_menuscript(node.content.current('data.json'), node.menuscript.current())

@app.route('/api/node/generate_audio/<int:node_id>/', methods=['POST'])
def api_node_generate_audio(node_id):
    node = save_node(node_id, request.json)
    node.audio.save({})  # create new snapshot
    if  not gen_audio(node.content.current('data.json'), node.audio.current()):
        return jsonify({'error': 'Failed to generate audio'}), 500
    return {'audioUrl': f'/api/node/download_audio/{node_id}/'}

@app.route('/api/node/download_audio/<int:node_id>/')
def api_node_download_audio(node_id):
    node = db.session.get(Node, node_id)
    return send_file(node.audio.current('audio.mp3'), as_attachment=True)

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True)

