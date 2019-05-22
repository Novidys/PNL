#!/usr/bin/env python
# coding : utf-8
import threading
import logging
import queue
import chardet
import re

from PNL.credentials import Credential
from PNL.exceptions import *


class Worker(threading.Thread):
    name = 'WorkerThread'

    def __init__(self, fifo_in, fifo_out):
        self.stop = threading.Event()
        self.logger = logging.getLogger('pnl')
        self.fifo_in = fifo_in
        self.fifo_out = fifo_out
        threading.Thread.__init__(self)

    @staticmethod
    def return_decoded_line(line):
        try:
            decoded_line = line.decode(encoding='utf-8').rstrip('\n').rstrip('\r')
        except UnicodeDecodeError:
            # We try to detect the charset
            dict_charset = chardet.detect(line)

            if dict_charset['confidence'] > 0.60:
                try:
                    decoded_line = line.decode(encoding=dict_charset['encoding']).rstrip('\n').rstrip('\r')
                except ValueError:
                    raise PNLNonWorkingEncoding('Charset', dict_charset['encoding'], 'Confidence %f',
                                                dict_charset['confidence'])
            else:
                raise PNLUnknownEncoding

        return decoded_line

    def run(self):
        total_credential = 0
        emailonly_credential = 0
        noemail_credential = 0
        while True:
            try:
                filename = self.fifo_in.get(block=False)
            except queue.Empty:
                self.logger.info('Worker has finished')
                self.fifo_out.put((total_credential, noemail_credential, emailonly_credential))
                break
            else:
                line_number = 1
                with open(filename, 'rb') as fd:
                    for line in fd:

                        if self.stop.isSet():
                            break

                        try:
                            decoded_line = self.return_decoded_line(line)
                        except PNLUnknownEncoding as e:
                            self.logger.info('Unknown encoding in %s on line %d' % (filename, line_number))
                            continue
                        except PNLNonWorkingEncoding as e:
                            self.logger.info('Error in charset detection. %s', str(e))
                            continue

                        try:
                            credential = Credential(decoded_line)
                        #except PNLNonPosixEmailAddress:
                        #    self.logger.info('Non POSIX email address in %s on line %d' % (filename, line_number))
                        except PNLOnlyEMail:
                            self.logger.info('Only email found in %s on line %d' % (filename, line_number))
                            emailonly_credential += 1
                        except PNLNoEmailFound:
                            self.logger.info('No email found in before sep %s on line %d' % (filename, line_number))
                            noemail_credential += 1
                        except PNLHashSuspected:
                            self.logger.info('Hash suspected in %s on line %d' % (filename, line_number))
                        else:
                            total_credential += 1

                        line_number += 1
                if self.stop.isSet():
                    self.logger.info('Worker has been asked to stop')
                    break
