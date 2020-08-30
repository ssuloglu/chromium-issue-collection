
# Owned
import folderops
from scraper import Scraper
from filereader import CsvFileReader as cr 

__author__ = 'Selma Suloglu'
__copyright__ = 'Copyright 2020'
__credits__ = ['Selma Suloglu']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Selma Suloglu'
__status__ = 'Dev'



# {code}
def collect_issues(key):
    """ Collects issues by creating a Scraper object

        Args:
            key (string): query key, either 'all' or 'CVE'
    """
    print(" [*] Collecting issues ...")
    return Scraper().collect_issues(key)
    

def process_issue_info(issues):
    """ Creates a dict where issue id is the key and issue_type the value

        Args:
            issues (list):  a list of issue data 
    """
    col_names = {'issue_id': None, 'issue_type': None}
    for cn in col_names:
        col_names[cn] = None if not cn in issues[0] else issues[0].index(cn)
    return {r[col_names['issue_id']]:r[col_names['issue_type']] for r in issues[1:]}
    
            
def collect_comments(key, filename=None):
    """ Collects comments for the list of issues in the filename
        If filename does not exist, first gathers issue data and
        then collects associated comments

        Args:
            filename (string): a csv file name including a set of issueids 
    """
    if not filename:
        # Collect issue data associated with CVEs
        filename = collect_issues(key)

    print(" [*] Collecting comments ...")
    if folderops.file_exist(filename):
        issues = process_issue_info(cr().read(filename))
        Scraper().collect_comments('one', issues)



if __name__ == "__main__":
    # Collect all issue ids
    collect_issues("all")
        
    # Collect comments with a given issue list
    collect_comments('CVE', 'inputs/sample_issue_list.csv')
    # Collect comments without an issue list
    collect_comments('CVE')

