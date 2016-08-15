Query Ratsit
============
Simple script for querying Ratsit.se to retrieve address information using
Firstname, Lastname, and Personal number.

Usage
*****
Running the program without any arguments, or with the ``-h`` or ``--help``
flags, show the following help message::

    usage: query_ratsit.py [-h] [-o OUTFILE] [-f FAILED] QUERY.CSV               
                                                                                 
    Query Ratsit.se for address information based on personal number and name.   
    Careful!                                                                     
                                                                                 
    positional arguments:                                                        
      QUERY.CSV             CSV file with first name(s), last name, personal     
                            number, on each row.                                 
                                                                                 
    optional arguments:                                                          
      -h, --help            show this help message and exit                      
      -o OUTFILE, --output OUTFILE                                               
                            Output file to write query results to                
                            [successful_queries.csv]                             
      -f FAILED, --failed FAILED                                                 
                            Write failed queries to csv file [failed_queries.csv]

Input
*****
Input is a three-column CSV file::

    "Firstname","Lastname","YYYYMMDD-NNNN"

Missing fields are allowed. However, any missing fields lowers the probability
of finding a unique match (and thus being able to find an address).

Output
******
The main output is a four column CSV file::

    "Firstname","Lastname","YYYYMMDD-NNNN","Adress line 1\nAdress line 2"

The CSV file can easily be imported into e.g. Excel.  
In addition, an output file with all the failed queries is also created, making
it easy to manually go through all the queries which failed to find a unique
match in Ratsit.
