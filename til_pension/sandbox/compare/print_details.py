# -*- coding: utf-8 -*-

from til_pension.simulation import PensionSimulation
from til_pension.pension_legislation import PensionParam, PensionLegislation

def run_to_print(data, yearsim):
    param = PensionParam(yearsim, data)
    legislation = PensionLegislation(param)
    simul_til = PensionSimulation(data, legislation)
    simul_til.profile_evaluate(to_check=False)

run_to_print(data_to_print, yearsim)
