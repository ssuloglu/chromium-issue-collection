""" 
FileReader abstract class and inherited classes specific to
a file format: 
    (*) JsonFileReader - .json
    (*) TxtFileReader - .txt   
    (*) CsvFileReader - .csv 
"""

# Generic/Built-in
import os
import json
import csv
from abc import ABCMeta, abstractmethod


__author__ = 'Selma Suloglu'
__copyright__ = 'Copyright 2019, DV8 Pipeline project'
__credits__ = ['Selma Suloglu']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Selma Suloglu'
__status__ = 'Dev'


# {code}
class FileReader():
    """
    Abstract class with two abstract methods to read files
    in different formats.
    """

    __metaclass__ = ABCMeta
    def __init__(self):
        pass

    def _check_file_exists(self, filename):
        """Check file exists or not
    
        Args:
            filename (string): file name.

        Returns:
            bool: True if file exists, False otherwise 

        """
        if not os.path.exists(filename):
            print('\n[-] ERROR: %s is not at the specified path! \
                Please check the filepath and filename...' 
                         %filename)
            return False
        return True

    @abstractmethod
    def read(self, filename):
        """reads the file content.
    
        Args:
            filename (string): file name.
        """
        pass


class JsonFileReader(FileReader):
    """ Read a json file. """
    def __init__(self):
        FileReader.__init__(self)


    def read(self, filename):
        content = None
        if self._check_file_exists(filename):
            with open(filename, 'r') as outfile:
                content = json.load(outfile)        
        return content


class TxtFileReader(FileReader):
    """ Read a txt file. """
    def __init__(self):
        FileReader.__init__(self)
        

    def read(self, filename, as_str=False):
        content = None
        if self._check_file_exists(filename):
            f = open(filename, 'r')
            content = [l.strip('\n\r ') for l in f.readlines()]
            f.close() 
        if as_str:
            return '\n'.join(content) 
        else:     
            return content


class CsvFileReader(FileReader):
    """ Read a csv file. """
    def __init__(self):
        FileReader.__init__(self)
        

    def read(self, filename, header=True):
        content = None
        if self._check_file_exists(filename):
            with open(filename) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',') 
                content = [row for row in csv_reader]       
        return content if header else content[1:]

