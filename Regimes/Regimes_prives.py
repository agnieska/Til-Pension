# -*- coding:utf-8 -*-
import math
from datetime import datetime

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from time_array import TimeArray
from pension_data import PensionData

from numpy import array, multiply
from pandas import Series

from regime import compare_destinie
from regime_prive import RegimePrive
from utils_pension import build_long_values, build_salref_bareme
from trimesters_functions import trim_ass_by_year, validation_trimestre, sali_in_regime, trim_mda, imput_sali_avpf

code_avpf = 8
code_chomage = 2
code_preretraite = 9
first_year_indep = 1972
first_year_avpf = 1972
    
class RegimeGeneral(RegimePrive):
    
    def __init__(self):
        RegimePrive.__init__(self)
        self.regime = 'RG'
        self.code_regime = [3,4]
        self.param_name_bis = 'prive.RG'
     
    def get_trimesters_wages(self, data, to_check=False):
        trimesters = dict()
        wages = dict()
        trim_maj = dict()
        to_other = dict()
        
        workstate = data.workstate
        sali = data.sali
        info_ind = data.info_ind
        
        salref = build_salref_bareme(self.P_longit.common, data.initial_date.year, data.datesim.year)
        trimesters['cot'], wages['cot'] = validation_trimestre(data, self.code_regime, salref)
        
        trimesters['ass'], _ = trim_ass_by_year(data, self.code_regime, compare_destinie)
        
        data_avpf = data.selected_dates(first_year_avpf)
        data_avpf.sali = imput_sali_avpf(data_avpf, code_avpf, self.P_longit, compare_destinie)
        salref = build_salref_bareme(self.P_longit.common, first_year_avpf, data.datesim.year)
        # Allocation vieillesse des parents au foyer : nombre de trimestres attribués 
        trimesters['avpf'], wages['avpf'] = validation_trimestre(data_avpf, code_avpf, salref)

        trim_maj['DA'] = trim_mda(info_ind, self.P, self.dateleg.year)

        if to_check is not None:
            to_check['DA_RG'] = ((trimesters['cot'] + trimesters['ass'] + trimesters['avpf']).sum(1) 
                                 + trim_maj['DA'])/4
        output = {'trimesters': trimesters, 'wages': wages, 'maj': trim_maj}
        return output, to_other

class RegimeSocialIndependants(RegimePrive):
    
    def __init__(self):
        RegimePrive.__init__(self)
        self.regime = 'RSI'
        self.code_regime = [7]
        self.param_name_bis = 'indep.rsi'

    def get_trimesters_wages(self, data, to_check=False):
        trimesters = dict()
        wages = dict()
        trim_maj = dict()
        to_other = dict()
        
        workstate = data.workstate
        sali = data.sali
        
        reduce_data = data.selected_dates(first=first_year_indep)
        salref = build_salref_bareme(self.P_longit.common, first_year_indep, data.datesim.year)
        trimesters['cot'], _ = validation_trimestre(reduce_data, self.code_regime, salref)

        nb_trim_ass, _ = trim_ass_by_year(reduce_data, self.code_regime, compare_destinie)
        trimesters['ass'] = nb_trim_ass
        wages['regime'] = sali_in_regime(workstate, sali, self.code_regime)
        trim_maj['DA'] = 0*trim_mda(data.info_ind, self.P, self.dateleg.year)
        if to_check is not None:
                to_check['DA_RSI'] = (trimesters['cot'].sum(1) + trim_maj['DA'])//4
        output = {'trimesters': trimesters, 'wages': wages, 'maj': trim_maj}
        return output, to_other