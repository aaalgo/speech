import os

HOME = os.path.dirname(os.path.abspath(__file__))

PORT = 18200
HOST = '0.0.0.0'

DATA_ROOT = os.path.join(HOME, 'data')

THUMB_WIDTH = 128
THUMB_HEIGHT = 96

DB_URI = 'mysql+mysqldb://speech:speech@localhost:3306/speech'

def deck_path (deck_id):
    return os.path.join(DATA_ROOT, str(deck_id))

def node_path (deck_id, node_id):
    return os.path.join(DATA_ROOT, str(deck_id), 'nodes', str(node_id))
