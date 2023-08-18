import os
import sys

class ArchiveSessiosStorage:
    def __init__(self, directory: str):
        self.directory = directory

        if not os.path.exists(directory):
            os.makedirs(directory)
