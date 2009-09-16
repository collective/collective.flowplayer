from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.flowplayer"""

    def afterSetUp(self):
        self.addProfile('collective.flowplayer:default')
        # put resource registry to debug mode to avoid cachekyes in tests
        self.portal.portal_css.setDebugMode(True)
        self.portal.portal_javascripts.setDebugMode(True)

layer = Layer([tcl_ptc.ptc_layer])
