#!/usr/bin/env python
# coding : utf-8
import threading
import logging
import queue
import chardet

from PNL.credentials import Credential
from PNL.exceptions import *

g_total_credential = 0
g_total_line = 0
g_emailonly_credential = 0
g_noemail_credential = 0


class RedisWorker(threading.Thread):

    def __init__(self, worker_id, stop_event, cred_event, condition, redis, fifo, channel):
        self.stop_event = stop_event
        self.logger = logging.getLogger('pnl')
        self.fifo = fifo
        self.redis = redis
        self.channel = channel
        self.cred_event = cred_event
        self.condition = condition
        threading.Thread.__init__(self, name='RedisWorkerThread'+str(worker_id))

    def run(self):
        cred_sent = 0
        while True:
            if self.stop_event.isSet():
                self.logger.info('Received stop event')
                break
            try:
                credential = self.fifo.get(block=False)
            except queue.Empty:
                if self.cred_event.isSet():
                    self.logger.info('Credential analysis is finished')
                    self.logger.info('Sent %d credentials to Redis' % cred_sent)
                    break
            else:
                self.redis.publish(self.channel, credential)
                cred_sent += 1
                if cred_sent % 10000 == 0:
                    self.logger.info('Sent %d credentials to Redis' % cred_sent)
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()


class CredentialWorker(threading.Thread):

    def __init__(self, worker_id, stop_event, files_event, condition, fifo_in, fifo_out, fifo_stats):
        self.stop = stop_event
        self.files_event = files_event
        self.logger = logging.getLogger('pnl')
        self.fifo_in = fifo_in
        self.fifo_out = fifo_out
        self.fifo_stats = fifo_stats
        self.condition = condition
        self.emailonly_credential = 0
        self.noemail_credential = 0
        self.total_line = 0
        self.total_credential = 0
        threading.Thread.__init__(self, name='CredentialWorkerThread'+str(worker_id))

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
                    raise PNLNonWorkingEncoding(dict_charset['encoding'], dict_charset['confidence'])
            else:
                raise PNLUnknownEncoding

        return decoded_line

    def run(self):
        while True:
            try:
                filename = self.fifo_in.get(block=False)
                self.logger.debug('Get filename %s' % filename)
            except queue.Empty:
                if self.files_event.isSet():
                    self.fifo_stats.put((self.total_line, self.total_credential, self.noemail_credential,
                                         self.emailonly_credential))
                    self.logger.debug('Filesystem analysis is finished')
                    break
            else:
                line_number = 1
                with open(filename, 'rb') as fd:
                    file_cred = 0
                    for line in fd:

                        if self.stop.isSet():
                            break

                        try:
                            decoded_line = self.return_decoded_line(line)
                        except PNLUnknownEncoding:
                            self.logger.info('Unknown encoding in %s on line %d' % (filename, line_number))
                        except PNLNonWorkingEncoding as e:
                            self.logger.info('Error in charset detection. Charset %s. Confidence %s' %
                                             (e.encoding, e.confidence))
                        else:
                            try:
                                credential = Credential(decoded_line)
                            #except PNLNonPosixEmailAddress:
                            #    self.logger.info('Non POSIX email address in %s on line %d' % (filename, line_number))
                            except PNLOnlyEMail:
                                self.logger.info('Only email found in %s on line %d' % (filename, line_number))
                                self.logger.debug(decoded_line)
                                self.emailonly_credential += 1
                            except PNLNoEmailFound:
                                self.logger.info('No email found before sep in %s on line %d' % (filename, line_number))
                                self.logger.debug(decoded_line)
                                self.noemail_credential += 1
                            except PNLHashSuspected:
                                self.logger.info('Hash suspected in %s on line %d' % (filename, line_number))
                                self.logger.debug(decoded_line)
                            else:
                                self.fifo_out.put(credential.return_credentials())
                                file_cred += 1
                                self.total_credential += 1
                                del credential
                        line_number += 1
                        self.total_line += 1
                    self.logger.info('Read %d lines in %s' % (line_number-1, filename))
                    self.logger.info('Found %d credentials in %s' % (file_cred, filename))
                if self.stop.isSet():
                    self.logger.info('Received stop event')
                    break
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
        self.logger.info('Worker has finished')
