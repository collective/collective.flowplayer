# -*- coding: utf-8 -*-
from plone.testing import z2
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.configuration import xmlconfig

import doctest


class FlowPlayerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.flowplayer
        xmlconfig.file('configure.zcml',
                       collective.flowplayer,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install collective.flowplayer
        applyProfile(portal, 'collective.flowplayer:default')

        # Put resource registry to debug mode to avoid cachekyes in tests
        portal.portal_css.setDebugMode(True)
        portal.portal_javascripts.setDebugMode(True)

        portal.acl_users.userFolderAddUser('admin', 'secret', ['Manager'], [])
        login(portal, 'admin')

        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory("Folder",
                             id="test-folder", title=u"Test Folder")


COLLECTIVE_FLOWPLAYER_FIXTURE = FlowPlayerLayer()

COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FLOWPLAYER_FIXTURE, ),
    name="FlowPlayer:Integration"
)
COLLECTIVE_FLOWPLAYER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FLOWPLAYER_FIXTURE, ),
    name="FlowPlayer:Functional"
)
COLLECTIVE_FLOWPLAYER_ROBOT_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FLOWPLAYER_FIXTURE, z2.ZSERVER_FIXTURE),
    name="FlowPlayer:Robot"
)


optionflags = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)
