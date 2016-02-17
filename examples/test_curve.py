"""Example how to make an acceptance curve and background model image.
"""
import numpy as np
from astropy.coordinates import Angle
from astropy.table import Table
from gammapy.datasets import gammapy_extra
from gammapy.background import EnergyOffsetBackgroundModel
from gammapy.utils.energy import EnergyBounds, Energy
from gammapy.data import DataStore
import pylab as pt
pt.ion()

def make_model():
    dir = str(gammapy_extra.dir) + '/datasets/hess-crab4-hd-hap-prod2'
    data_store = DataStore.from_dir(dir)
    obs_table = data_store.obs_table

    ebounds = EnergyBounds.equal_log_spacing(0.1, 100, 100, 'TeV')
    offset = Angle(np.linspace(0, 2.5, 100), "deg")
    multi_array = EnergyOffsetBackgroundModel(ebounds, offset)
    multi_array.fill_obs(obs_table, data_store)
    multi_array.compute_rate()

    bgarray=multi_array.bg_rate
    energ_range = Energy([1, 10], 'TeV')
    bins = 10
    table = bgarray.acceptance_curve_in_energy_band(energ_range, bins)

    multi_array.write('energy_offset_array.fits', overwrite=True)
    table.write('acceptance_curve.fits', overwrite=True)

def make_image():
    pass


def plot_model():
    multi_array = EnergyOffsetBackgroundModel.read('energy_offset_array.fits')
    table = Table.read('acceptance_curve.fits')
    pt.figure(1)
    multi_array.counts.plot_image()
    pt.figure(2)
    multi_array.livetime.plot_image()
    pt.figure(3)
    multi_array.bg_rate.plot_image()

    pt.plot(table["offset"], table["Acceptance"])
    pt.xlabel("offset (deg)")
    pt.ylabel("Acceptance (s-1)")

    input()


if __name__ == '__main__':
    # make_model()
    plot_model()