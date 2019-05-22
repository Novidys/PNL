#!/usr/bin/env python
# coding : utf-8


class PNLNonPosixEmailAddress(Exception):
    pass


class PNLOnlyEMail(Exception):
    pass


class PNLUnknownEncoding(Exception):
    pass


class PNLNonWorkingEncoding(Exception):
    pass


class PNLNoEmailFound(Exception):
    pass

class PNLHashSuspected(Exception):
    pass
