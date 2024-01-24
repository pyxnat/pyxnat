from pyxnat import Interface
from pyxnat.core import downloadutils as du
from pyxnat.tests import skip_if_no_network
import tempfile

central = Interface('https://www.nitrc.org/ir', anonymous=True)


@skip_if_no_network
def test_download():
    s = central.select.project('dlbs').subject('XNAT_S04207')
    e = s.experiment('XNAT_E16269')
    du.download(dest_dir=tempfile.gettempdir(),
                instance=e.scans(),
                extract=True,
                removeZip=True)
