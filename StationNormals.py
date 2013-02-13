#! /usr/bin/python

import re

class StationNormals:
    """Load and provide access to station 1981-2010 climate normal data.

    This class parses and provides access to station data from the 1981-2010 climate normal data
    data set.  Specifically, it loads the .txt files of the sort found at
    http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/station
    (for example, the file 
    http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/station/USC00018809.normals.txt).

    This class does not read data over the internet; you have to download the file first.  Usage
    is like this:

        s = StationNormals("USC00018809.normals.txt")

        print s.meta['Station Name']
        print s.normals['Temperature-Related']['Daily']['dly-tmax-normal']

    s.meta is a dict containing the station metadata, and s.normals is a dict
    containing the normals data.  The structure of s.normals is like this:

       s.normals = {
          'Temperature-Related' : {
             'Monthly' : {
               'mly-tmax-normal' :  [652, 691, 758, 843, 936, 1023, 1038, 1013,  971,  862,  730,  632],
               'mly-tavg-normal' :  [527, 559, 613, 685, 778,  863,  905,  888,  839,  723,  599,  512],
               ...
             },
             'Daily' : {
               'dly-tmax-normal' :  [
                                       [630,631,633,634,636,637,...,672], # jan
                                       [673,674,675,676,677,678,...,716], # feb
                                       [718,720,723,725,728,730,...,800], # and so on
                                       [803,805,808,811,814,816,...,885],
                                       [888,891,894,897,901,904,...,984],
                                       [987,991,994,997,999,1002,...,1046],
                                       [1046,1047,1047,1047,1047,1047,...,1023],
                                       [1022,1021,1020,1019,1019,1018,...,1004],
                                       [1003,1002,1001,999,998,996,...,925],
                                       [921,917,914,910,906,902,...,801],
                                       [797,793,788,784,779,775,...,664],
                                       [661,657,654,650,647,644,...,629]
                                     ],
               ...
             },
          'Precipitation-Related' : {
              ... similar to the above ...
          }
        }
      }

    Data values are stored as integers, and correspond exactly to the numbers in the .txt file; no scaling has been applied,
    although the completeness flags (the 'S', 'R', 'P', etc suffixes on each value in the .txt file) have been removed, and
    the values converted to ints."""


    months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

    def __init__(self, file):
        self.meta = {}
        self.normals = {}
        self.loadfromfile(file)

    @staticmethod
    def trim_from_end(array, value):
        while len(array) > 0 and array[len(array)-1]==value:
            array.pop()
        return array

    @staticmethod
    def month_index(month):
        for i in range(0,len(StationNormals.months)):
            if StationNormals.months[i] == month:
                return i
        return -1

    @staticmethod
    def transform_data(type, values):
        return [int(re.sub(r'[A-Z]$', '', val)) for val in values]

    def loadfromfile(self, file):
        f = open(file, 'r')
        type = None
        frequency = None
        variable = None
        for line in [x.strip() for x in f]:
            m = re.match(r'^([a-zA-Z][^:]*):([^:]+)$', line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                self.meta[key] = val
                continue
            m = re.match(r'^(.*)\s+Normals\s*$', line)
            if m:
                type = m.group(1).strip()
                if type not in self.normals:
                    self.normals[type] = {}
                continue
            # this next regex matches any line starting with a capitalized word that ends with 'ly':
            m = re.match(r'^([A-Z]\S+ly)\b', line)
            if m:
                frequency = m.group(1)
                if type == None:
                    raise Exception("encountered new frequency '%s' not in any normals type" % frequency)
                if frequency not in self.normals[type]:
                    self.normals[type][frequency] = {}
                continue
            # only proceed beyond here if we have a valid type
            if type == None:
                continue
            if frequency == 'Daily':
                columns = re.split(r'\s+', line)
                if (len(columns) == 33) and (columns[1] in StationNormals.months):
                    variable = columns.pop(0) # remove 1st column; it's the variable name
                    if variable not in self.normals[type][frequency]:
                        self.normals[type][frequency][variable] = [[]]*12
                if (len(columns) == 32) and (columns[0] in StationNormals.months):
                    month = columns.pop(0)
                    i = StationNormals.month_index(month)
                    if i < 0 or i >= 12:
                        raise Exception("unknown month: %s" % month)
                    self.normals[type][frequency][variable][i] = \
                        StationNormals.transform_data(type, StationNormals.trim_from_end(columns, '-8888'))
            if frequency == 'Monthly':
                columns = re.split(r'\s+', line)
                if len(columns) == 13:
                    variable = columns.pop(0) # remove 1st column; it's the variable name
                    self.normals[type][frequency][variable] = \
                        StationNormals.transform_data(type, StationNormals.trim_from_end(columns, '-8888'))
        f.close()
