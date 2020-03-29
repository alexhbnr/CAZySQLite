########################################################################
# Infer taxonomic information from NCBI taxonomic IDs
#
# Alex Huebner, 27/03/2020
########################################################################

from ete3 import NCBITaxa
import pandas as pd

global Args

ncbi = NCBITaxa()


def update_taxonomy(update):
    """Update NCBI taxonomy database used by ete3."""
    if update:
        ncbi.update_taxonomy_database()


def taxonomy_lineage(tid):
    """Infer the taxonomic names for a taxonomic ID."""
    # try:
    lineage_tids = ncbi.get_lineage(tid)
    lineage_ranks = {v: k for k, v in ncbi.get_rank(lineage_tids).items()}
    lineage_names = ncbi.get_taxid_translator(lineage_tids)
    return [lineage_names[lineage_ranks[r]] if r in lineage_ranks else ""
            for r in ['superkingdom', 'phylum', 'class', 'order', 'family',
                      'genus', 'species']] + [lineage_tids[-1]]
    # except ValueError:
        # return [""] * 7


def infer_taxonomy_lineage(taxids):
    """Infer the taxonomic lineages for all tax IDs stated on CAZy website."""
    lineages = [taxonomy_lineage(int(tid)) for tid in taxids]
    return pd.DataFrame(lineages, columns=['superkingdom', 'phylum', 'class',
                                           'order', 'family', 'genus',
                                           'species', 'NCBItaxid']) \
        .assign(taxid=taxids)[['taxid', 'NCBItaxid', 'superkingdom', 'phylum',
                                'class', 'order', 'family', 'genus',
                                'species']]
