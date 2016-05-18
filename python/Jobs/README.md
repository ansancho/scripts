##  trabajo_basura.py
### Explanation

Trabajo basura (Crap Job) is a little scrapper script which its main purpose is gathering
all the directory of technological companies listed on http://trabajobasura.info. 
 After the directory is retrieved, the script order the info by rating (default) or popularity and
exports all info to a csv file for later analysis.


    usage: trabajo_basura.py [-h] [-u USER] [-p PASSW] [-d] [-f [FILE]] [-s {r,R,p,P}]
    Grabs full directory of companies from http://trabajobasura.info and export them to a csv file

    optional arguments:
        -h, --help            show this help message and exit
        -u USER, --user USER  Registered username. In case the page asks you for credentials
        -p PASSW, --passw PASSW User password
        -d, --debug           Print debug messages
        -f [FILE], --file [FILE] Output csv file, if ommitted then will be junkcs.csv
        -s {r,R,p,P}, --sort {r,R,p,P} Sort companies by rate (r) or popularity (p)



