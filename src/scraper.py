# Generic/Built-in
import os
import re
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

# Owned
import folderops
from filereader import TxtFileReader as tfr


__author__ = 'Selma Suloglu'
__copyright__ = 'Copyright 2020'
__credits__ = ['Selma Suloglu']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Selma Suloglu'
__status__ = 'Dev'


# {code}
class Scraper():
    # parameters for each query
    queries = {
        'CVE': {
            'explanation' : 'issues associated with CVE ids',
            'project' : 'Chromium',
            'urlbase' : 'https://bugs.chromium.org/p/chromium/issues/list?q=CVE&can=1&colspec=ID%20Component%20Status%20Owner%20Summary%20Type&start=',
            'headers' : {
                'issue': ['issue_id','issue_owner','issue_status','issue_type','issue_components',
                          'issue_title'], 
            },
            'output_filename' : 'outputs/CVE/chromium_issues_associated_with_CVEs.csv'
        } ,
        'all': {
            'explanation' : 'all issues (id)',
            'project' : 'Chromium',
            'headers' : {
                'issue': ['issue_id', 'issue_type']
            },
            'urlbase': 'https://bugs.chromium.org/p/chromium/issues/list?colspec=ID%20Type&start=',
            'output_filename': 'outputs/all/chromium_all_issueids.csv'
        },
        'one': {
            'explanation' : 'issue metadata and comments',
            'project' : 'Chromium',
            'headers' : {
                'issue': ['issue_id', 'issue_owner', 'issue_cc', 'issue_status', 'issue_type', 
                          'issue_components', 'issue_title', 'issue_details'],
                'comment': ['comment_id', 'comment_datetime', 'comment_author', 'comment_message']
            },
            'urlbase' : 'https://bugs.chromium.org/p/chromium/issues/detail?id=',
            'output_filename' : 'outputs/one/issue_comments.csv'
        }
    }

    # regex patterns
    issue_header_pattern = re.compile('Issue\s(\d+):(.+)')
    issue_count_pattern = re.compile('.*of\s(\d+)') 
    comment_pattern = re.compile('Comment\s(\d+)(\s*by\s*(.+)\son\s(.+\s(AM|PM)\sGMT(\+|-)\d+))?') 

    css_selector_by_header = {'issue_id' : '.col-id',
                              'issue_type' : '.col-type',
                              'issue_title' : '.col-summary',
                              'issue_owner' : '.col-owner',
                              'issue_status' : '.col-status',
                              'issue_components' : '.col-component'}

    def __init__(self):
        """ Creates the output file with headers

            Args:
                key (string) : key to be used to find query content in self.queries dictionary 
        """
        pass


    def __get_issue_uri(self, issue_id):
        """ Returns issue uri 

            Args:
                issue_id (string) : id of the issue         
        """
        return self.queries[self.key]['urlbase'] + issue_id


    def __expand_shadow_element(self, element):
        """ Expands shadow element and returns its content

            Args:
                element (selenium.webdriver.chrome.webdriver.WebDriver) : web element         
        """
        return self.driver.execute_script('return arguments[0].shadowRoot', element)

    
    def __expand_shadow_element_by_tag_name(self, root, tag_name):
        """ Find root element by 'tag_name' and returns associated shadow element 

           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element          
                tag_name (string) : html tag name 
        """
        try:
            element = root.find_element_by_tag_name(tag_name)
            return self.driver.execute_script('return arguments[0].shadowRoot', element)
        except NoSuchElementException:
            print ('Unable to locate element - %s'%tag_name)
            return None


    def __expand_shadow_element_by_css_selector(self, root, css_selector):
        """ Finds root element by 'css_selector' and returns associated shadow element 

           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element          
                css_selector (string) : html css selector
        """
        try:
            element = root.find_element_by_css_selector(css_selector)
            return self.driver.execute_script('return arguments[0].shadowRoot', element)
        except NoSuchElementException:
            print ('Unable to locate element - %s'%css_selector)
            return None


    def __get_page(self, tag_name):
        """ Extracts top shadow element of the page and returns shadow element content for 
            'mr-issue-page' tag name where issue metadata and comments are located 
        
            Args:
                tag_name (string): html tag name
        """
        app_root = self.__expand_shadow_element_by_tag_name(self.driver, 'mr-app')
        return self.__expand_shadow_element_by_tag_name(app_root, tag_name)


    def __get_issue_id_and_title(self, root):
        """ Returns a dictionary with issue id and title by extracting shadow root 
            with the tag name 'mr-issue-header' or an empty dictionary if there is no 
            root element found.  
           
           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element
        """
        issue_header_root = self.__expand_shadow_element_by_tag_name(root, 'mr-issue-header')
        issue_header = issue_header_root.find_element_by_css_selector('div.main-text>h1').text

        m = re.match(self.issue_header_pattern, issue_header) 
        if m:
            return {
                'issue_id' : m.group(1),
                'issue_title' : m.group(2).strip('\n\r ')
            }
        else:
            return {
                'issue_id' : '',
                'issue_title' : ''
            }


    def __get_issue_details(self, root):
        """ Returns issue details 
           
           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element
        """
        description_root = self.__expand_shadow_element_by_tag_name(root, 'mr-description')
        content_root = self.__expand_shadow_element_by_tag_name(description_root, 'mr-comment-content')   
        lines = content_root.find_elements_by_css_selector('.line')
        return ' '.join([l.text.strip('\n\r ') for l in lines]) 


    def __process_text(self, text):
        """ Replaces new lines with '||' in the given 'text' 
           
           Args:
                text (string) : text 
        """
        return text.replace('\n', '||')


    def __get_issue_metadata(self, root):
        """ Extracts issue metadata: issue_owner, issue_cc, issue_status and issue_components
           
           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element  
        """
        issue_metadata_root = self.__expand_shadow_element_by_tag_name(root, 'mr-issue-metadata')
        issue_data_root = self.__expand_shadow_element_by_tag_name(issue_metadata_root, 'mr-metadata')

        return {
            'issue_owner' : self.__process_text(issue_data_root.find_element_by_css_selector ('.row-owner>td').text),
            'issue_cc' : self.__process_text(issue_data_root.find_element_by_css_selector ('.row-cc>td').text),
            'issue_status' : self.__process_text(issue_data_root.find_element_by_css_selector ('.row-status>td').text),
            'issue_components' : self.__process_text(issue_data_root.find_element_by_css_selector ('.row-components>td').text)
        }


    def __get_comments(self, root):
        """ Extracts comments from the shadow element tagged with 'mr-comment-list'
            and collects comment_id, comment_datetime, comment_author and comment_message
            for each comment 

           Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element 
        """
        comments_root = self.__expand_shadow_element_by_tag_name(root, 'mr-comment-list')

        list_of_comments = comments_root.find_elements_by_tag_name('mr-comment')
        print ('[*] %d comments' %len(list_of_comments))
        comments = []
        for c in list_of_comments:
            comment_root = self.__expand_shadow_element(c)
            comment_header = comment_root.find_element_by_css_selector('div>div').text.replace('\n', ' ')
            
            m = re.match(self.comment_pattern, comment_header)
            blank_comment = { 'comment_id':'', 'comment_datetime':'', 
                              'comment_author':'', 'comment_message': ' '} 
            if m:
                comment_id = m.group(1).strip('\n\r ')
                if not 'Deleted' in comment_header:
                    message_root = self.__expand_shadow_element_by_css_selector(comment_root, '.comment-body>mr-comment-content')
                    lines = message_root.find_elements_by_css_selector('.line')

                    comments.append({
                        'comment_id': comment_id,
                        'comment_datetime': m.group(4).strip('\n\r '),
                        'comment_author' : m.group(3).strip('\n\r '),
                        'comment_message': ' '.join([l.text.strip('\n\r ') for l in lines]) 
                    })
                else:
                    blank_comment['comment_id'] = comment_id
                    comments.append(blank_comment) 
            else:
                comments.append(blank_comment) 
        return comments


    def __get_headers(self):
        """ Returns headers
        """
        headers = self.queries[self.key]['headers']
        return (headers['comment'] if 'comment' in headers else []) + headers['issue']  


    def __append_to_csv(self, content):
        """ Appends content to the output file (csv)

           Args:
                content (dict) : issue details and a list of comments 
        """
        csv_content = []

        # csv headers
        headers = self.queries[self.key]['headers']

        issue_content = [content[ih] for ih in headers['issue']] if 'issue' in headers else []
        if 'comment' in headers:
            for c in content['comments']:
                csv_content.append([c[ch] for ch in headers['comment']] + issue_content) 
        else:
            csv_content.append(issue_content)

        print(csv_content)
        with open(self.queries[self.key]['output_filename'], 'a+') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(csv_content)


    def __create_output_file(self):
        """ Creates the output file with headers

            Args:
                key (string) : key to be used to find query content in self.queries dictionary 
        """
        filename = self.queries[self.key]['output_filename']
        folderops.create_folder(os.path.dirname(os.path.abspath(filename)))
        folderops.create_file(self.queries[self.key]['output_filename'], 
                              headers=self.__get_headers())


    def __get_issue_count(self, root, tag_name):
        """ Returns issue count

            Args:
                root (selenium.webdriver.chrome.webdriver.WebDriver) : web element
                tag_name (string): html tag name        
        """
        s = root.find_element_by_tag_name(tag_name).text.strip('\n\r ')
        m = re.match(self.issue_count_pattern, s) 
        return int(m.group(1)) if m else None 
        

    def __create_driver(self, url):
        """ Creates web driver for the "url"

            Args:
                url (string) : url
        """
        self.driver = webdriver.Chrome()
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                ec.visibility_of_element_located((By.TAG_NAME, 'mr-app'))
            )
            self.driver.implicitly_wait(25)
        except TimeoutException as e:
            print ('[-] TimeoutException')
            self.driver.quit()
        except StaleElementReferenceException as e:
            print ('[-] StaleElementReferenceException')
            self.driver.quit()


    def __extract_list(self, rows):
        """ Extracts issue info wrt specified headers

            Args:
                rpos (int) : list of rows 
        """
        # headers specified for self.key
        headers = self.queries[self.key]['headers']['issue']

        data = {}                        
        for r in rows:
            for h in headers:
                text = r.find_element_by_css_selector(self.css_selector_by_header[h]).text.strip('\n\r ')
                data[h] = self.__process_text(text) if h=='issue_components' else text 
            self.__append_to_csv(data)


    def __collect_issue_list_in_single_page(self, ind):
        """ Extracts issue list and if there is a next page, recursively
            calls itself with the next index (ind) 

            Args:
                ind (int) : index 
        """
        self.__create_driver(self.queries[self.key]['urlbase']+str(ind))

        list_root = self.__get_page('mr-list-page')
        if not list_root: 
            self.driver.quit()
            return
        
        issue_list_root = self.__expand_shadow_element_by_css_selector(list_root, 'mr-issue-list')
        issue_list_table = issue_list_root.find_elements_by_css_selector('table tbody tr')
        self.__extract_list(issue_list_table)
        
        # if "Next>" then scrape the next page
        next_page_exist = 'Next ›' in [e.text for e in list_root.find_elements_by_tag_name('a')]
        self.driver.quit()

        # Collect issues for the next page
        self.__collect_issue_list_in_single_page(ind+100)


    def collect_issues(self, key):
        """ Collects issues with the parameters found in self.queries dict

           Args:
                key (string) : key to be used to find query content in self.queries dictionary
        """
        self.key = key
        self.__create_output_file()

        print('[+] Scraping content for query: <<'+ self.key +'>>')
        self.__collect_issue_list_in_single_page(0)
        return self.queries[self.key]['output_filename'] if self.key in self.queries else '' 
        
        
    def collect_comments(self, key, issues):
        """ Collects issues with the parameters found in self.queries dict

           Args:
                key (string) : key to be used to find query content in self.queries dictionary
                issues (list) : a list of issue ids
        """
        self.key = key
        self.__create_output_file()
    
        for issue_id in issues:
            issue_uri = self.__get_issue_uri(issue_id) 
            print ('[*] Scraping %s' %issue_uri)
            
            self.__create_driver(issue_uri)
            if not self.driver: 
                continue

            issue_root = self.__get_page('mr-issue-page')
            if not issue_root: 
                self.driver.quit()
                continue
             
            issue_details_root = self.__expand_shadow_element_by_css_selector(issue_root, 
                                                                              '.container-issue-content>.main-item')
            if not issue_details_root: 
                self.driver.quit()
                continue
        
            content = self.__get_issue_id_and_title(issue_root)
            content.update(self.__get_issue_metadata(issue_root))
            content['issue_type'] = issues[issue_id]
            content['issue_details'] = self.__get_issue_details(issue_details_root)
            content['comments'] = self.__get_comments(issue_details_root)

            self.driver.quit()
            self.__append_to_csv(content)
            