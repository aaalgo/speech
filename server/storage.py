import os
import json
import datetime

class VersionedDirectory:
    def __init__(self, root: str, create: bool = False):
        self.root = root
        if create and not os.path.exists(root):
            os.makedirs(root)
    
    def snapshots (self):
        snapshots = []
        for item in os.listdir(self.root):
            if (item != "current") and os.path.isdir(os.path.join(self.root, item)):
                snapshots.append(item)
        snapshots.sort()
        return snapshots

    def save (self, data):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        snapshot = os.path.join(self.root, timestamp)
        os.makedirs(snapshot, exist_ok=False)
        self.__save__(snapshot, data)
        if os.path.exists(os.path.join(self.root, 'current')):
            os.remove(os.path.join(self.root, 'current'))
        os.symlink(snapshot, os.path.join(self.root, 'current'))

    def load(self, snapshot: str = None):
        if snapshot is None:
            snapshot = 'current'
        path = os.path.join(self.root, snapshot)
        if not os.path.exists(path):
            return None
        return self.__load__(path)

    def current(self):
        return os.path.join(self.root, 'current')

    def __save__(self, snapshot: str, data):
        with open(os.path.join(snapshot, 'data.json'), 'w') as f:
            json.dump(data, f)
    
    def __load__(self, snapshot: str):
        with open(os.path.join(snapshot, 'data.json'), 'r') as f:
            return json.load(f)
    
class DataDirectory(VersionedDirectory):
    def __init__(self, root: str, create: bool = False):
        super().__init__(root, create)

