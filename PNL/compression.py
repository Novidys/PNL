#!/usr/bin/env python
# coding : utf-8
from io import BytesIO
import zipfile


class Archive(object):
    def __init__(self, extension):
        self.extension = extension.tolower()
        self.memory_file = BytesIO()

    def uncompress(self, in_memory=True):
        if self.extension == 'zip':
            pass

