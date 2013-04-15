# -*- coding: utf-8 -*-
import os
import time
import unittest

testfile_home = os.path.join(os.path.dirname(__file__))
file_handle = open(testfile_home + '/barsandtone.flv', 'rb')


class TestMetadataProfiling(unittest.TestCase):

    def testFLVHeader(self):
        tt = time.time()
        # import
        from collective.flowplayer.flv import FLVHeader
        # parse
        file_handle.seek(0)
        flvparser = FLVHeader()
        flvparser.analyse(file_handle.read(1024))
        assert((288, 360) == (flvparser.getHeight(), flvparser.getWidth()))
        print ' (parse with FLVHeader: {0:0.6f})'.format(time.time() - tt)

    def testHachoir(self):
        tt = time.time()
        # import
        import collective.flowplayer.metadata_extraction as metaex
        # parse
        file_handle.seek(0)
        metadata = metaex.parse_raw(file_handle)
        file_handle.close()
        assert((288, 360) == metaex.scale_from_metadata(metadata))
        print ' (parse with metadata_extraction: {0:0.6f})'.format(
            time.time() - tt)
