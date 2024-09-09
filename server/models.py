import os
import enum
import json
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, Double,Text, BLOB, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Session, reconstructor
from sqlalchemy.schema import PrimaryKeyConstraint
import base64
import cv2
from storage import DataDirectory
import image
import config
    
class Base (DeclarativeBase):
    pass

class Deck (Base):
    __tablename__ = 'deck'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    create_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    update_time = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    nodes = relationship('Node', back_populates='deck')
    meta = None

    @reconstructor
    def init_data (self):
        self.path = None
        self.meta = None
        if not self.id is None:
            self.path = config.deck_path(self.id)
            self.meta = DataDirectory(os.path.join(config.deck_path(self.id), 'meta'), create=True)

    def load (self):
        data = self.meta.load()
        data['id'] = self.id
        data['name'] = self.name
        return data

    def save (self, data):
        self.meta.save(data)

class Node (Base):
    __tablename__ = 'node'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id = mapped_column(Integer, ForeignKey('deck.id'))
    deck = relationship('Deck', back_populates='nodes')
    create_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    update_time = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    @reconstructor
    def init_data (self):
        self.path = None
        self.content = None
        self.slide = None
        self.script = None
        self.audio = None
        self.video = None
        if not self.id is None: 
            self.path = config.node_path(self.deck_id, self.id)
            self.content = DataDirectory(os.path.join(self.path, 'content'), create=True)
            self.slide = DataDirectory(os.path.join(self.path, 'slide'), create=True)
            self.script = DataDirectory(os.path.join(self.path, 'script'), create=True)
            self.audio = DataDirectory(os.path.join(self.path, 'audio'), create=True)
            self.video = DataDirectory(os.path.join(self.path, 'video'), create=True)
            self.menuscript = DataDirectory(os.path.join(self.path, 'menuscript'), create=True)

    def load (self):
        data = {
            'id': self.id,
            'deck_id': self.deck_id,
            'thumb': image.read_base64(self.slide.current('thumb.png')),
            'image': image.read_base64(self.slide.current('slide.png')),    
            } 
        content = self.content.load()
        if content is not None:
            data.update(content)
        script = self.script.load()
        if script is not None:
            data.update(script)
        menuscript = self.menuscript.load()
        if menuscript is not None:
            data.update(menuscript)
        audio_path = self.audio.current('audio.mp3')
        if os.path.exists(audio_path):
            data['audioUrl'] = f'/api/node/download_audio/{self.id}/'
        video_path = self.video.current('video.mp4')
        if os.path.exists(video_path):
            data['videoUrl'] = f'/api/node/download_video/{self.id}/'
        return data

    @staticmethod
    def base64_thumb (deck_id, node_id):
        thumb_path = os.path.join(config.node_path(deck_id, node_id), 'slide', 'current', 'thumb.png')
        return image.read_base64(thumb_path)
    

if __name__ == '__main__':
    #from sqlalchemy import create_engine
    #engine = create_engine('sqlite:///db.sqlite')
    #Base.metadata.create_all(engine)
    pass

