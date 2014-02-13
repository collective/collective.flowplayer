from collective.flowplayer.uninstall import all as uninstall_all


def uninstall(portal):
    uninstall_all(portal)
    return "Ran all uninstall steps."
