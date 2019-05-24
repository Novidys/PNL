#!/usr/bin/env python
# coding : utf-8


class PNLNonPosixEmailAddress(Exception):
    pass


class PNLOnlyEMail(Exception):
    pass


class PNLUnknownEncoding(Exception):
    pass


class PNLNonWorkingEncoding(Exception):
    def __init__(self, encoding, confidence):
        self.encoding = encoding
        self.confidence = confidence


class PNLNoEmailFound(Exception):
    pass

class PNLHashSuspected(Exception):
    pass


class PNLNoStatsReceived(Exception):
    pass
