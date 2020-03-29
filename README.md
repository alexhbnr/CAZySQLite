SQLite database for CAZy.org
================

  - [Preparation of database file prior to
    usage](#preparation-of-database-file-prior-to-usage)
  - [Structure of the SQLite
    database](#structure-of-the-sqlite-database)
      - [Table “genomes”](#table-genomes)
      - [Table “taxids”](#table-taxids)
      - [Table “ncbitaxonomy”](#table-ncbitaxonomy)

This repository provides the information stored at <http://www.cazy.org>
as computer-readable SQLite database. For this, it scrapes information
stored as HTML tables on the website into tabular data using Python and
makes the information available as a SQLite database.

Additionally to the information provided at <http://www.cazy.org>, it
adds further information, e.g. on the taxonomy of each species, or
cross-identification of proteins to the eggNOG database.

## Preparation of database file prior to usage

The repository comes with the pre-generated SQLite database file. Due to
the size limitations of GitHub, the SQLite database is compressed using
[bzip2](https://www.sourceware.org/bzip2/). In order to use it, we have
to decompress it locally using

``` bash
bunzip2 -k CAZyme_genomes.db.bz2
```

The decompressed SQLite database can be used like any regular SQLite
database.

## Structure of the SQLite database

Here, I will use the scripting language R to illustrate the content of
the SQLite database. For this, we will use the two R packages
[DBI](https://cran.r-project.org/web/packages/DBI/index.html) and
[RSQLite](https://cran.r-project.org/web/packages/RSQLite/index.html).

``` r
# Check if packages for connecting to the database are available
if (!all(c("RSQLite", "DBI") %in% installed.packages())) {
    install.packages(c("DBI", "RSQLite"))
}
library(RSQLite)
library(DBI)
library(magrittr)
```

We can open a connection to the database using the function `dbConnect`:

``` r
conn <- dbConnect(RSQLite::SQLite(), "CAZyme_genomes.db")
```

By using `dbListTables`, we get an overview of the tables present in the
database:

``` r
dbListTables(conn)
```

    ## [1] "genomes"      "ncbitaxonomy" "taxids"

### Table “genomes”

The table **“genomes”** contains the information which CAZyme genes are
present in each genome. It has four different columns:

  - *name*: the name of the genome
  - *protein*: the name of the protein
  - *family*: the CAZy enzyme classification
  - *refAcc*: the NCBI GenBank reference ID of the protein

An example of the output looks like follows:

    ##                       name                   protein family     refAcc
    ## 1  Absiella argi JCM 30884          Aargi30884_00940   GH23 BBK21191.1
    ## 2  Absiella argi JCM 30884          Aargi30884_01330    CE4 BBK21230.1
    ## 3  Absiella argi JCM 30884          Aargi30884_01410    GT4 BBK21238.1
    ## 4  Absiella argi JCM 30884          Aargi30884_01810   GH23 BBK21278.1
    ## 5  Absiella argi JCM 30884          Aargi30884_03230   GT51 BBK21420.1
    ## 6  Absiella argi JCM 30884          Aargi30884_03530   GH23 BBK21450.1
    ## 7  Absiella argi JCM 30884          Aargi30884_07470   GH23 BBK21844.1
    ## 8  Absiella argi JCM 30884          Aargi30884_07780   GT51 BBK21875.1
    ## 9  Absiella argi JCM 30884 Aargi30884_08810 (Bgla_1)    GH1 BBK21978.1
    ## 10 Absiella argi JCM 30884          Aargi30884_09640    CE4 BBK22061.1

### Table “taxids”

The table **“taxids”** contains the information on the taxonomy of the
genomes provided by the cazy.org website. It has three different
columns:

  - *name*: the name of the genome
  - *taxid*: the NCBI taxonomy ID provided by cazy.org
  - *superkingdom*: the superkingdom category it was classified in on
    cazy.org

An example of the output looks like follows:

    ##                                   name   taxid superkingdom
    ## 1              Absiella argi JCM 30884 1671597     bacteria
    ## 2                 Absiella sp. 9CBEGH2 2583452     bacteria
    ## 3       Acaryochloris marina MBIC11017  329726     bacteria
    ## 4  Acetoanaerobium sticklandii DSM 519  499177     bacteria
    ## 5          Acetobacter aceti TMW2.1153     435     bacteria
    ## 6       Acetobacter ascendens LMG 1590  481146     bacteria
    ## 7     Acetobacter ascendens SRCM101447  481146     bacteria
    ## 8     Acetobacter ghanensis LMG 23848T  431306     bacteria
    ## 9          Acetobacter orientalis FAN1  146474     bacteria
    ## 10   Acetobacter oryzifermentans SLV-7 1633874     bacteria

### Table “ncbitaxonomy”

The table **“ncbitaxonomy”** contains the information on the taxonomic
lineage of each taxonomic ID available in the table **“taxids”**
provided by NCBI. It has nine columns:

  - *taxid*: the NCBI taxonomy ID provided by cazy.org
  - *NCBItaxid*: the corresponding NCBI taxonomy ID; different from
    *taxid* when updated in the NCBI taxonomy database
  - *superkingdom* to *species*: the name of the taxonomic ranks for the
    lineage defined by the NCBI taxonomy ID

An example of the output looks like follows:

    ##      taxid NCBItaxid superkingdom         phylum               class              order                family           genus                     species
    ## 1  1671597   1671597     Bacteria     Firmicutes    Erysipelotrichia Erysipelotrichales   Erysipelotrichaceae        Absiella               Absiella argi
    ## 2  2583452   2583452     Bacteria     Firmicutes    Erysipelotrichia Erysipelotrichales   Erysipelotrichaceae        Absiella        Absiella sp. 9CBEGH2
    ## 3   329726    329726     Bacteria  Cyanobacteria                        Synechococcales    Acaryochloridaceae   Acaryochloris        Acaryochloris marina
    ## 4   499177    499177     Bacteria     Firmicutes          Clostridia      Clostridiales Peptostreptococcaceae Acetoanaerobium Acetoanaerobium sticklandii
    ## 5      435       435     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter           Acetobacter aceti
    ## 6   481146    481146     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter       Acetobacter ascendens
    ## 7   431306    431306     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter       Acetobacter ghanensis
    ## 8   146474    146474     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter      Acetobacter orientalis
    ## 9  1633874   1633874     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter Acetobacter oryzifermentans
    ## 10 2500548   2500548     Bacteria Proteobacteria Alphaproteobacteria   Rhodospirillales      Acetobacteraceae     Acetobacter        Acetobacter oryzoeni
