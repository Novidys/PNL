#!/usr/bin/env python
# coding : utf-8
import re

from PNL.exceptions import *


class Credential(object):
    def __init__(self, line):
        self._line = line
        self._length_line = len(line)
        self._posixemail = None
        self._email = None
        self._password = None
        self._length_email = None
        self._separator = None
        self._username = None
        self._domain = None
        self.extract_posix_email()
        self.extract_separator()
        self.extract_email()
        self.extract_password()

    def __setattr__(self, name, value):
        if name == '_email' and value:
            self._length_email = len(value)
        object.__setattr__(self, name, value)

    def extract_posix_email(self):
        posix_email = r'(?:[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&\'\.*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")\.?@(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-zA-Z0-9-]*[a-zA-Z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'

        m = re.match(posix_email, self._line)

        if m:
            self._posixemail = m.group(0)
        else:
            self._posixemail = ''

    def extract_separator(self):
        #if self._length_email == self._length_line:
        #    raise PNLOnlyEMail
        #self._separator = self._line[self._length_email]
        #if self._separator not in [':', ';']:
        #    print(self._line)
        dict_separators = {}
        for separator in ['|', ';', ':']:
            pos = self._line.find(separator)
            if pos > -1:
                dict_separators[separator] = self._line.find(separator)
        if dict_separators:
            self._separator = min(dict_separators, key=dict_separators.get)
        else:
            raise PNLOnlyEMail

    def extract_email(self):
        self._email = self._line.split(self._separator, 1)[0]
        if '@' not in self._email:
            raise PNLNoEmailFound
        self._username, self._domain = self._email.rsplit('@', maxsplit=1)

    def extract_password(self):
        payload = self._line.split(self._separator, maxsplit=1)[1]
        if self._separator in payload:
            # TODO : look for hash values in there
            # TODO : separator could be a simple character in the password
            # TODO : payload could be a simple hash
            # TODO : payload could be a hash and a password
            #if len(payload) > 31:
            #    raise PNLHashSuspected
            self._password = payload
        else:
            self._password = payload
