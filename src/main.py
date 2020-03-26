#!/usr/bin/env python
########################################################################
# Scrapes CAZy.org and converts data into SQLite3 database
#
# Alex Huebner, 25/03/2020
########################################################################

import argparse
import os
import re
import sys

from bs4 import BeautifulSoup
import json
import pandas as pd
import sqlite3
import urllib3


def create_dirs(fn):
    """Create missing directories for output fn."""
    if not os.path.isdir(os.path.dirname(fn)) and os.path.dirname(fn) != "":
        os.makedirs(os.path.dirname(fn), exist_ok=True)


def soup_extract_links(url, linkclass):
    """Process URL using BeautifulSoup and find all elements of linkclass."""
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')
    return soup.find_all(class_=linkclass,
                         attrs={'href': re.compile("^http://")})


def soup_process_species(url, datavalue):
    """Parse species site into table."""
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')

    # Species name
    species_name = soup.find_all(class_="titre_cazome")[0].string
    # NCBI taxid
    species_taxid = soup.find_all(target="ncbitaxid")[0].string
    if not re.search("unreleased", str(soup)):
        # Generate Pandas DataFrame
        df = pd.read_html(str(soup.find_all("table")[-1]),
                          skiprows=1, header=0)[0] \
            .dropna()
        df.columns = ['protein', 'family', 'refAcc']
        df['name'] = species_name
        return [df[['name', 'protein', 'family', 'refAcc']],
                (species_name, species_taxid, datavalue)]
    else:
        return [None, (species_name, species_taxid, datavalue)]


def download_genomes(config, datavalue):
    """Download genomes from cazy.org.

    Parameters:
    = config: dictionary with information on urls specific to the CAZy website
    - datavalue: specify with subset of CAZYGENOMES to download, e.g. bacteria

    Returns: list of two Pandas DataFrames
    - table with proteins per genome
    - table with genome names and taxids

    """
    url = config['CAZYBASEURL'] + "/" + config['CAZYGENOMES'][datavalue]

    protein_list = []
    taxid_list = []
    for subpage in soup_extract_links(url, "nav1"):
        for species in soup_extract_links(subpage.get('href'), "nav"):
            proteins, taxid = soup_process_species(species.get('href'),
                                                   datavalue)
            if proteins is not None:
                protein_list.append(proteins)
            taxid_list.append(taxid)

    protein_df = pd.concat(protein_list)
    taxid_df = pd.DataFrame(taxid_list,
                            columns=["name", "taxid", "superkingdom"])
    return [protein_df, taxid_df]


def main():
    """Scrape content of cazy.org and store in SQLite3 database."""
    # Load config
    with open(Args['config'], "rt") as configfile:
        config = json.load(configfile)

    # Download genomes
    if not Args['nogenomes']:
        genome_categories = config['CAZYGENOMES']
        if Args['noarchaea']:
            del genome_categories['archaea']
        if Args['nobacteria']:
            del genome_categories['bacteria']
        if Args['noeukaryotes']:
            del genome_categories['eukaryotes']
        if Args['noviruses']:
            del genome_categories['viruses']
    if len(genome_categories.keys()) > 0:
        create_dirs(Args['output'])
        protein_dfs = []
        taxids_dfs = []
        for cat in genome_categories.keys():
            print(f"Download genome category {cat}", file=sys.stderr)
            proteins, taxids = download_genomes(config, cat)
            protein_dfs.append(proteins)
            taxids_dfs.append(taxids)
        print("Write protein list to SQLite3 database", file=sys.stderr)
        pd.concat(protein_dfs) \
            .to_sql("genomes", sqlite3.connect(Args['output']),
                    index=False, if_exists=Args['tablemode'])
        print("Write taxid list to SQLite3 database", file=sys.stderr)
        pd.concat(taxids_dfs) \
            .to_sql("taxids", sqlite3.connect(Args['output']),
                    index=False, if_exists=Args['tablemode'])
    else:
        print("All genome categories were excluded from downloading. At least"
              " one genome category must be enabled.", file=sys.stderr)
        sys.exit(1)


# Argument parser
Parser = argparse.ArgumentParser(description='Scrapes content of cazy.org '
                                 'and stores in SQLite3 database.')
Parser.add_argument('-c', '--config',
                    default=os.path.dirname(__file__) + '/../config.json',
                    help='JSON config file with cazy.org URLS')
Parser.add_argument('-o', '--output', help='filename for SQLite3 database')
# Add arguments specific for SQLite storage
sqlite = Parser.add_argument_group("SQLite3 database storage")
sqlite.add_argument('--tablemode', default="append",
                    choices=['append', 'replace', 'fail'],
                    help='how to behave when table already exists [append]')
# Add arguments specific for genomes download
genomes = Parser.add_argument_group("Download genome information")
genomes.add_argument('--nogenomes', action='store_true',
                     help='do not download genomes [download all genomes]')
genomes.add_argument('--noarchaea', action='store_true',
                     help='do not download archaeal genomes')
genomes.add_argument('--nobacteria', action='store_true',
                     help='do not download bacterial genomes')
genomes.add_argument('--noeukaryotes', action='store_true',
                     help='do not download eukaryote genomes')
genomes.add_argument('--noviruses', action='store_true',
                     help='do not download viral genomes')
Args = vars(Parser.parse_args())

if __name__ == '__main__':
    main()
