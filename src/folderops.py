# Generic/Built-in
import os
import shutil 


__author__ = 'Selma Suloglu'
__copyright__ = 'Copyright 2020'
__credits__ = ['Selma Suloglu']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Selma Suloglu'
__status__ = 'Dev'


# {code}
def file_exist(filename):
    """ Checks if the file exist

        Args:
            filename (string): name of the file 
    """
    return os.path.exists(filename)


def create_file(filename, headers=None):
    """ Creates a file if it doesn't exist
        Writes headers to newly created file if
        'headers' is provided

        Args:
            filename (string): name of the file
            headers (list of string) : lis of column names  
    """
    if not os.path.exists(filename):
        f = open(filename, 'w')
        if headers:
            f.write(','.join(headers)+'\n')
        f.close()


def create_folder(folder_path):
    """ Creates a folder in 'folder_path' if
        it does not exist 

        Args:
            folder_path (string): folder path    
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
       
       
def recreate_folder(folder_path):
    """ Deletes existing folder with its sub folders and 
        Creates a folder in 'folder_path' 

        Args:
            folder_path (string): folder path    
    """
    if not os.path.exists(folder_path): 
        os.makedirs(folder_path)
    else:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)


def copy_file(src, dest):
    """ Copies 'src' file to 'dest' 

        Args:
            src (string): file name to be copied from 
            dest (string): file name to be copied to
    """
    shutil.copyfile(src, dest)          


def list_files(folder_path):
    """ Extracts the list of files in 'folder_path'
        which does not start with '.' 

        Args:
            folder_path (string): folder path    
    """
    return [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if not filename.startswith('.')]
        

def get_file_extension(filename, separator='.'):
    """ Extracts extension of the given file ('filename') 

        Args:
            filename (string): name of the file
            separator (string): denominator    
    """
    return filename[filename.rfind(separator)+1:]
