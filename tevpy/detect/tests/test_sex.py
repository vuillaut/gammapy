# Licensed under a 3-clause BSD style license - see LICENSE.rst
import subprocess
import tempfile
import pytest
#from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from ...data import poisson_stats_image
from ..sex import sex

try:
    #subprocess.call('sex')
    process = subprocess.Popen('sex', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    HAS_SEX = True
except OSError:
    HAS_SEX = False


# TODO: this test doesn't work in the test runner, because get_pkg_data_filename
# doesn't work ... on my machine it returns a filename which doesn't exist:
# /private/var/folders/sb/4qv5j4m90pz1rw7m70rj1b1r0000gn/T/astropy-test-Zg88hJ/lib.macosx-10.8-intel-2.7/tevpy/detect/tests/../../data/poisson_stats_image/counts.fits.gz
@pytest.mark.skipif('not HAS_SEX')
def test_sex():
    """Run SExtractor an example image and check number of detected sources"""
    #filename = get_pkg_data_filename('../../data/poisson_stats_image/counts.fits.gz')
    #filename = poisson_stats_image(return_filenames=True)
    data = poisson_stats_image()
    filename = tempfile.mktemp('.fits')
    fits.writeto(filename, data=data)
    catalog, checkimage = sex(filename)
    assert len(catalog) == 35
    assert checkimage.data.max() == 35