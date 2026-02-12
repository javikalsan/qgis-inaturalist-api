import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)


from .inaturalist import Inaturalist


def classFactory(iface):
    return Inaturalist(iface)
