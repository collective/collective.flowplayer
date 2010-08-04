import unittest
import time
import os

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
        print 'parse with FLVHeader: ' + str(time.time() - tt)

    def testHachoir(self):
        tt = time.time()
        # import
        import collective.flowplayer.metadata_extraction as metaex
        # parse
        file_handle.seek(0)
        metadata = metaex.parse_raw(file_handle)
        assert((288, 360) == metaex.scale_from_metadata(metadata))
        print 'parse with metadata_extraction: ' + str(time.time() - tt)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMetadataProfiling))
    return suite
