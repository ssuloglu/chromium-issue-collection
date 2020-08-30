
# Chromium issue collection 
Issue Collector for Chromium project


## Overview

Welcome to `Chromium issue collection` project that provides scripts 
* given the query to obtain the list of issues
* given the list of issue ids to extract issue metadata and associated comments 
for [Chromium project](https://www.chromium.org/Home) from [its offical issue tracker](https://bugs.chromium.org/p/chromium/issues/list).   

## Dynamic Scraping
 To collect issues, their metadata and associated comments we used dynamic web scraping tool [Selenium](https://selenium-python.readthedocs.io). 

# Dependencies

## Configure and Manage Your Environment with Anaconda

## Overview
Using Anaconda consists of the following:

1. Install [`anaconda`](https://www.anaconda.com/distribution/) on your computer, by selecting the latest Python version for your operating system. If you already have `conda` installed, you should be able to skip this step and move on to step 2.

2. Create and activate * a new `conda` [environment](http://conda.pydata.org/docs/using/envs.html) with `chromium_issue_collection.yml` file provided.


#### Git and version control
These instructions also assume you have `git` installed for working with Github from a terminal window, but if you do not, you can download that first with the command:
```
conda install git
```

**Now, we're ready to create our local environment!**

1. Clone the repository, and navigate to the downloaded folder. This may take a minute or two to clone due to the included image data.
```
git clone <github project webaddress>.git
cd chromium-issue-collection
```

2. Navigate to `src/` folder and change `<username>` with your current user name in `chromium_issue_collection.yml` file  
```
	prefix: /Users/<username>/opt/anaconda3/envs/chromium_issue_collection
```

3. Create (and activate) a new environment, named `chromium_issue_collection` with Python 3.8. If prompted to proceed with the install `(Proceed [y]/n)` type y.

	- __Linux__ or __Mac__: 
	```
	conda env create -f chromium_issue_collection.yml
	conda activate chromium_issue_collection
	```
	- __Windows__: 
	```
	conda env create --name chromiumIssueCollection --file=chromium_issue_collection.yml
	activate chromiumIssueCollection
	```
	For conda cheatsheet: https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf

4. Download Chrome Driver from [here](https://sites.google.com/a/chromium.org/chromedriver/home) and add path to ChromeDriver to your `PATH`

5. Customize `scraper.py` script if you want to add a new query or change an existing one.

To add a new query, you need to append a new key and values into `queries` dictionary:    

```
'<key>': {
            'explanation' : '<explanation of the query>',
            'project' : '<project name>',
            'urlbase' : '<base url>',
            'headers' : {
                '<key>': <list of columns>, 
            },
            'output_filename' : '<output csv file name>'
        } 
```

6. Customize `run_scraper.py` script by changing function calls in `__main__` function. 


## Running Code Locally
To run scraper, navigate to `src` folder and run the script.
```
cd path/to/src/
python run_scraper.py
```
