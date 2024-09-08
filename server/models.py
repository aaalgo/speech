import os
import enum
import json
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, Double,Text, BLOB, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Session
from sqlalchemy.schema import PrimaryKeyConstraint
import cv2
from storage import DataDirectory
import image
import config

class DeckData (DataDirectory):
    # The deck folder contains:
    #   - meta/             -- versioned
    #   - nodes/{id}/       -- each node, versioned
    def __init__(self, id, create: bool = False):
        super().__init__(os.path.join(config.deck_path(id), 'meta'), create)

class NodeData (DataDirectory):
    def __init__(self, deck_id, node_id, create: bool = False):
        # root is path to deck/nodes/{id}
        root = os.path.join(config.deck_path(deck_id), 'nodes', str(node_id))
        super().__init__(root, create)

class SlideData (DataDirectory):
    def __init__(self, node_snapshot_dir: str, create: bool = False):
        # root is path to deck/nodes/{id}/{snapshot}/slide
        root = os.path.join(node_snapshot_dir, 'slide')
        super().__init__(root, create)

class ScriptData (DataDirectory):
    def __init__(self, node_snapshot_dir: str, create: bool = False):
        # root is path to deck/nodes/{id}/{snapshot}/script
        root = os.path.join(node_snapshot_dir, 'script')    
        super().__init__(root, create)
        
class AVData (DataDirectory):
    def __init__(self, script_snapshot_dir: str, create: bool = False):
        # root is path to deck/nodes/{id}/{snapshot}/script/{snapshot}/av
        root = os.path.join(script_snapshot_dir, 'av')
        super().__init__(root, create)        

    
class Base (DeclarativeBase):
    pass

class Deck (Base):
    __tablename__ = 'deck'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    create_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    update_time = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    nodes = relationship('Node', back_populates='deck')

    @property
    def data (self):
        if not getattr(self, '__data__', None):
            self.__data__ = DeckData(self.id, create=True)
        return self.__data__

    def load (self):
        data = self.data.load()
        data['id'] = self.id
        data['name'] = self.name
        return data

    def save (self, data):
        self.data.save(data)

class Node (Base):
    __tablename__ = 'node'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id = mapped_column(Integer, ForeignKey('deck.id'))
    deck = relationship('Deck', back_populates='nodes')
    create_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    update_time = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def data (self):
        if self.__data is None:
            self.__data = NodeData(self.deck_id, self.id, create=True)
        return self.__data

    def load (self, updateThumb=False):
        data = self.data.load()
        data['id'] = self.id
        data['deck_id'] = self.deck_id
        data['thumb'] = self.base64_thumb()
        return data

    def save (self, data):
        self.data.save(data)
    
    def base64_thumb (self):
        thumb_path = os.path.join(self.data.current(), 'slide', 'current', 'thumb.png')
        if not os.path.exists(thumb_path):
            thumb = image.text(data['content'])
        else:
            thumb = cv2.imread(thumb_path, cv2.IMREAD_COLOR)
        return image.base64_encode(thumb)

if __name__ == '__main__':
    #from sqlalchemy import create_engine
    #engine = create_engine('sqlite:///db.sqlite')
    #Base.metadata.create_all(engine)
    pass

