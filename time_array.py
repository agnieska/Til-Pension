# -*- coding: utf-8 -*-

class TimeArray(object):
    
    def __init__(self, array, dates):
        self.array = array
        self.dates = dates
        
    def selected_dates(self, first, last, date_type='year', inplace=False):
        ''' La table d'input dont les colonnes sont des dates est renvoyées amputée 
            des années postérieures à first (first incluse) 
            et antérieures strictement à last 
            date_type est month ou year
            '''
        array = self.array
        dates = self.dates
        if date_type == 'year':
            if first:
                first = 100*first + 1
            if last:
                last = 100*last + 1
        array_dates = [i  
                       for i in range(len(dates))
                            if first <= dates[i] and dates[i] < last
                        ]
        dates = [dates[i] for i in array_dates]
        if inplace == True:
            self.array = array[:,array_dates]
            self.dates = dates
        else:
            return TimeArray(array[:,array_dates], dates)
    