from pyxnat import Interface
from pyxnat.core import downloadutils as du
from pyxnat.tests import skip_if_no_network
import tempfile

central = Interface('https://www.nitrc.org/ir', anonymous=True)


@skip_if_no_network
def test_download():
    s = central.select.project('cs_schizbull08').subject('xnat_S02636')
    e = s.experiment('xnat_E02685')
    du.download(dest_dir=tempfile.gettempdir(),
                instance=e.scans(),
                extract=True,
                removeZip=True)
