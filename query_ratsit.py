#!/usr/bin/env python3.5
# Query Ratsit.se for address information based on 
# Swedish personal number and name.
# Fredrik Boulund 2016


from sys import argv, exit
import csv
import logging
import argparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def parse_args(argv):
    """
    Parse arguments
    """
    desc = "Query Ratsit.se for address information based on personal number and name. Careful!"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("QUERY", metavar="QUERY.CSV", 
            help="CSV file with first name(s), last name, personal number, on each row.")
    parser.add_argument("-o", "--output", metavar="OUTFILE", dest="outfile",
            default="successful_queries.csv",
            help="Output file to write query results to [%(default)s]")
    parser.add_argument("-f", "--failed", dest="failed",
            default="failed_queries.csv",
            help="Write failed queries to csv file [%(default)s]")

    if len(argv) < 2:
        parser.print_help()
        exit()

    return parser.parse_args()


def query_ratsit(firstname, lastname, pnr):
    """
    Make HTTP queries to Ratsit.se using first name, last name, and personal number.

    Returns:
        address, string     Two-line address for the requested person.
    """

    ratsit_url = "https://www.ratsit.se/sok/avancerat/person?"
    
    payload = {"fnamn":firstname,
               "enamn":lastname,
               "pnr":pnr}

    logger.debug("Querying Ratsit for: %s, %s, %s", firstname, lastname, pnr)

    r = requests.get(ratsit_url, params=payload)

    #print(r.url)
    #print(r.status_code)
    #print(r.headers)
    #print(r.content)
    #print(r.text)

    search_soup = BeautifulSoup(r.content, "html.parser")
    search_results = search_soup.find_all("a", class_="search-list-content")

    if len(search_results) > 1:
        logger.debug("Found more than 1 result for ('%s', '%s', '%s')", firstname, lastname, pnr)
        return ""

    # Search was successful, but we need to open another webpage to parse
    # the full address including postal code.
    logger.debug("Fetching address page...")
    address_url = search_results[0]["href"]
    r_address = requests.get("https://www.ratsit.se"+address_url)
    
    address_soup = BeautifulSoup(r_address.content, "html.parser")
    address_result = address_soup.find("address")

    line1 = address_result.contents[0]
    line2 = address_result.contents[2]

    return "\n".join([line1, line2])



def parse_queryfile(queryfile):
    """
    Parse CSV query file.
    """
    with open(queryfile) as csvfile:
        csvreader = csv.reader(csvfile)
        for idx, row in enumerate(csvreader, start=1):
            try:
                firstname, lastname, pnr = row
            except ValueError:
                logger.warning("Could not parse row %s, skipping...", idx)
                continue
            yield firstname, lastname, pnr


def write_query_results(results, outputfile):
    """
    Write Ratsit query result to csv.
    """
    with open(outputfile, "w") as outcsv:
        outwriter = csv.writer(outcsv)
        for result in results:
            outwriter.writerow(result)


def main(queryfile, outfile, failedfile):
    results = []
    failed = []
    logger.info("Starting processing of queries from '%s'", queryfile)
    for records, data in enumerate(parse_queryfile(queryfile), start=1):
        firstname, lastname, pnr = data
        address = query_ratsit(firstname, lastname, pnr)
        if address:
            results.append((firstname, lastname, pnr, address))
        else:
            failed.append((firstname, lastname, pnr))
        if not records % 200:
            logger.info("Processed %s queries", records)
    logger.info("Processed %s records, writing results to '%s' and '%s'", records, outfile, failedfile)
    write_query_results(results, outfile)
    write_query_results(failed, failedfile)


if __name__ == "__main__":
    options = parse_args(argv)
    main(options.QUERY, options.outfile, options.failed)
