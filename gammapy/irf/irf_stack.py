# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import numpy as np
from astropy.units import Quantity
from ..irf import EffectiveAreaTable, EnergyDispersion

__all__ = [
    'IRFStacker',
]

log = logging.getLogger(__name__)


class IRFStacker(object):
    r"""
    Stack instrument response functions
    
    Compute mean effective area and the mean energy dispersio for a given for a
    given list of instrument response functions. Results are stored as
    attributes.

    The stacking of :math:`j` elements is implemented as follows.  :math:`k`
    and :math:`l` denote a bin in reconstructed and true energy, respectively.

    .. math::

        \epsilon_{jk} =\left\{\begin{array}{cl} 1, & \mbox{if
            bin k is inside the energy thresholds}\\ 0, & \mbox{otherwise} \end{array}\right.

        \overline{t} = \sum_{j} t_i

        \overline{\mathrm{aeff}}_l = \frac{\sum_{j}\mathrm{aeff}_{jl}
            \cdot t_j}{\overline{t}}

        \overline{\mathrm{edisp}}_{kl} = \frac{\sum_{j} \mathrm{edisp}_{jkl}
            \cdot \mathrm{aeff}_{jl} \cdot t_j \cdot \epsilon_{jk}}{\sum_{j} \mathrm{aeff}_{jl}
            \cdot t_j}

    Parameters
    ----------
    list_arf: list
        list of `~gammapy.irf.EffectiveAreaTable`
    list_livetime: list
        list of `~astropy.units.Quantity` (livetime)
    list_rmf: list
        list of `~gammapy.irf.EnergyDispersion`
    list_low_threshold: list
        list of low energy threshold, optional for effective area mean computation
    list_high_threshold: list
        list of high energy threshold, optional for effecitve area mean computation


    """

    def __init__(self, list_arf, list_livetime, list_rmf=None,
                 list_low_threshold=None, list_high_threshold=None):
        self.list_arf = list_arf
        self.list_livetime = Quantity(list_livetime)
        self.list_rmf = list_rmf
        self.list_low_threshold = list_low_threshold
        self.list_high_threshold = list_high_threshold
        self.stacked_aeff = None
        self.stacked_edisp = None

    def stack_aeff(self):
        """
        Compute mean effective area
        """
        nbins = self.list_arf[0].energy.nbins
        aefft = Quantity(np.zeros(nbins), 'cm2 s')
        livetime_tot = np.sum(self.list_livetime)

        for i, arf in enumerate(self.list_arf):
            aeff_data = arf.evaluate(fill_nan=True)
            aefft_current = aeff_data * self.list_livetime[i]
            aefft += aefft_current

        stacked_data = aefft / livetime_tot
        self.stacked_aeff = EffectiveAreaTable(energy=self.list_arf[0].energy,
                                               data=stacked_data.to('cm2'))

    def mean_rmf(self):
        """
        Compute mean energy dispersion
        """
        reco_bins = self.list_rmf[0].e_reco.nbins
        true_bins = self.list_rmf[0].e_true.nbins

        aefft = Quantity(np.zeros(true_bins), 'cm2 s')
        temp = np.zeros(shape=(reco_bins, true_bins))
        aefftedisp = Quantity(temp, 'cm2 s')

        for i, rmf in enumerate(self.list_rmf):
            aeff_data = self.list_arf[i].evaluate(fill_nan=True)
            aefft_current = aeff_data * self.list_livetime[i]
            aefft += aefft_current
            edisp_data = rmf.pdf_in_safe_range(self.list_low_threshold[i],
                                               self.list_high_threshold[i])

            aefftedisp += edisp_data.transpose() * aefft_current

        stacked_edisp = np.nan_to_num(aefftedisp / aefft)
        self.stacked_edisp = EnergyDispersion(e_true=self.list_rmf[0].e_true,
                                              e_reco=self.list_rmf[0].e_reco,
                                              data=stacked_edisp.transpose())