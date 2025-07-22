def classFactory(iface):
    from .photogrammetry_tools import PhotogrammetryToolsPlugin
    return PhotogrammetryToolsPlugin(iface)