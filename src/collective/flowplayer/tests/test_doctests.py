# -*- coding: utf-8 -*-
from plone.testing import layered
from collective.flowplayer.testing import optionflags
from collective.flowplayer.testing import \
    COLLECTIVE_FLOWPLAYER_FUNCTIONAL_TESTING
try:
    # Python 2.6
    import unittest2 as unittest
except ImportError:
    # Python 2.7 has unittest2 integrated in unittest
    import unittest
import doctest

tests = (
    'README.txt',
)

non_layered_tests = (
    'metadata_extraction.txt',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f,
                                      package='collective.flowplayer',
                                      optionflags=optionflags),
                 layer=COLLECTIVE_FLOWPLAYER_FUNCTIONAL_TESTING)
         for f in tests] +
        [doctest.DocFileSuite(f,
                              package='collective.flowplayer',
                              optionflags=optionflags)
         for f in non_layered_tests])
