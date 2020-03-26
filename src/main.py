#!/usr/bin/env python
########################################################################
# Scrapes CAZy.org and converts data into SQLite3 database
#
# Alex Huebner, 25/03/2020
########################################################################

import argparse
import os
import sqlite3
import sys

import json
import pandas as pd

import download
import utils


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
        utils.create_dirs(Args['output'])
        protein_dfs = []
        taxids_dfs = []
        for cat in genome_categories.keys():
            print(f"Download genome category {cat}", file=sys.stderr)
            proteins, taxids = download.download_genomes(config, cat)
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
