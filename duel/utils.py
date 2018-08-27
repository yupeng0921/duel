#!/usr/bin/env python


class AssembleError(Exception):

    def __init__(self, line_no, reason):
        message = '%d: %s' % (line_no, reason)
        super(AssembleError, self).__init__(message)
