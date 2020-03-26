########################################################################
# Functions related to downloading data from cazy.org
#
# Alex Huebner, 25/03/2020
########################################################################

from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib3


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
    print(species_name)
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


