SQLite database for CAZy.org
================

This repository provides the information stored at <http://www.cazy.org>
as computer-readable SQLite database. For this, it reads information
stored as HTML tables on the website into tabular data interpretable by
Python and makes the information available as a SQLite database.

# Preparation of database file prior to usage

The repository comes with the pre-generated SQLite database file. Due to
the size limitations of GitHub, the SQLite database is compressed using
[bzip2](https://www.sourceware.org/bzip2/). In order to use it, we have
to decompress it locally using

``` bash
bunzip2 -k CAZyme_genomes.db.bz2`
```

The decompressed SQLite database can be used like any regular SQLite
database.

# Structure of the SQLite database

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

    ## [1] "genomes" "taxids"

## Table “genomes”

The table **“genomes”** contains the information which CAZyme genes are
present in each genome. It has four different columns:

``` r
dbListFields(conn, "genomes")
```

    ## [1] "name"    "protein" "family"  "refAcc"

  - *name*: the name of the genome
  - *protein*: the name of the protein
  - *family*: the CAZy enzyme classification
  - *refAcc*: the NCBI GenBank reference ID of the protein

An example of the output looks like follows:

``` r
dbReadTable(conn, "genomes") %>%
head(10)
```

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

## Table “taxids”

The table **“taxids”** contains the information on taxonomic information
of the genomes. It has three different columns:

``` r
dbListFields(conn, "taxids")
```

    ## [1] "name"         "taxid"        "superkingdom"

  - *name*: the name of the genome
  - *taxid*: the NCBI taxonomy ID
  - *superkingdom*: the superkingdom category it was classified in on
    cazy.org

An example of the output looks like follows:

``` r
dbReadTable(conn, "taxids") %>%
head(10)
```

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
