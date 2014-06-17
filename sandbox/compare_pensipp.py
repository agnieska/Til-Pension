# -*- coding: utf-8 -*-

import pandas as pd

from CONFIG_compare import pensipp_comparison_path
from simulation import PensionSimulation
from pension_legislation import PensionParam, PensionLegislation
from load_pensipp import load_pensipp_data, load_pensipp_result
first_year_sal = 1949 


def compare_til_pensipp(pensipp_comparison_path, var_to_check_montant, var_to_check_taux, threshold):
    result_pensipp = load_pensipp_result(pensipp_comparison_path, to_csv=True)
    result_til = pd.DataFrame(columns = var_to_check_montant + var_to_check_taux, index = result_pensipp.index)
    result_til['yearliq'] = -1
    for yearsim in range(2004,2005):
        print(yearsim)
        data_bounded = load_pensipp_data(pensipp_comparison_path, yearsim, first_year_sal)
        param = PensionParam(yearsim, data_bounded)
        legislation = PensionLegislation(param)
        simul_til = PensionSimulation(data_bounded, legislation)
        result_til_year = simul_til.profile_evaluate(to_check=True)
        id_year_in_initial = [ident for ident in result_til_year.index if ident in result_til.index] 
        assert (id_year_in_initial == result_til_year.index).all()
        result_til.loc[result_til_year.index, :] = result_til_year
        result_til.loc[result_til_year.index, 'yearliq'] = yearsim

    def _check_var(var, threshold, var_conflict, var_not_implemented):
        if var not in result_til.columns:
            print("La variable {} n'est pas bien implémenté dans Til".format(var))
            var_not_implemented['til'] += [var]
        if var not in result_pensipp.columns:
            print("La variable {} n'est pas bien implémenté dans Pensipp".format(var))
            var_not_implemented['pensipp'] += [var]
        to_compare = (result_til['yearliq']!= -1)
        til_compare = result_til.loc[to_compare,:]
        til_var = til_compare.loc[:, var].fillna(0)
        pensipp_var = result_pensipp.loc[to_compare,var].fillna(0)
        if (til_var == 0).all():
            var_not_implemented['til'] += [var]
        if (pensipp_var == 0).all():
            var_not_implemented['pensipp'] += [var]
        conflict = ((til_var.abs() - pensipp_var.abs()).abs() > threshold)
        if conflict.any():
            var_conflict += [var]
            print u"Le calcul de {} pose problème pour {} personne(s) sur {}: ".format(var, sum(conflict), sum(result_til['yearliq'] == 2004))
            print pd.DataFrame({
                "TIL": til_var[conflict],
                "PENSIPP": pensipp_var[conflict],
                "diff.": til_var[conflict].abs() - pensipp_var[conflict].abs(),
                "year_liq": til_compare.loc[conflict, 'yearliq']
                }).to_string()
            #relevant_variables = relevant_variables_by_var[var]
    var_conflict = []
    var_not_implemented = {'til':[], 'pensipp':[]}
    for var in var_to_check_montant:
        _check_var(var, threshold['montant'], var_conflict, var_not_implemented)
    for var in var_to_check_taux:
        _check_var(var, threshold['taux'], var_conflict, var_not_implemented)
    no_conflict = [variable for variable in var_to_check_montant + var_to_check_taux
                        if variable not in var_conflict + var_not_implemented.values()]  
    print( u"Avec un seuil de {}, le calcul est faux pour les variables suivantes : {} \n Il est mal implémenté dans : \n - Til: {} \n - Pensipp : {}\n Il ne pose aucun problème pour : {}").format(threshold, var_conflict, var_not_implemented['til'], var_not_implemented['pensipp'], no_conflict)   


if __name__ == '__main__':    

    var_to_check_montant = [ u'pension_RG', u'salref_RG', u'DA_RG', u'DA_RSI', 
                            u'nb_points_arrco', u'nb_points_agirc', u'pension_arrco', u'pension_agirc',
                            u'DA_FP', u'pension_FP',
                            u'n_trim_RG', 'N_CP_RG', 'n_trim_FP'
                            ] 
    var_to_check_taux = [u'taux_RG', u'surcote_RG', u'decote_RG', u'CP_RG',
                         u'taux_FP'
                          ]
    threshold = {'montant' : 1, 'taux' : 0.05}
    import logging
    import sys
    logging.basicConfig(format='%(funcName)s(%(levelname)s): %(message)s', level = logging.INFO, stream = sys.stdout)
    compare_til_pensipp(pensipp_comparison_path, var_to_check_montant, var_to_check_taux, threshold)

#    or to have a profiler : 
#    import cProfile
#    import re
#    command = """compare_til_pensipp(input_pensipp, output_pensipp, var_to_check_montant, var_to_check_taux, threshold)"""
#    cProfile.runctx( command, globals(), locals(), filename="profile_run_compare")