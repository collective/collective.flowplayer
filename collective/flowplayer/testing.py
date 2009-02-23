from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.flowplayer"""

    def afterSetUp(self):
        self.addProfile('collective.flowplayer:default')

layer = Layer([tcl_ptc.ptc_layer])
