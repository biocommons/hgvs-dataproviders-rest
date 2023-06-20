# uta-rest

Rest interface for [UTA](https://github.com/biocommons/uta).

The uta database is used by [hgvs](https://github.com/biocommons/hgvs) to perform many of its sequence manipulation functions. The hgvs library includes tools to normalize, validate, and map sequence variants (among other functionalities). In order for hgvs to access transcript info needed for such work, it uses the uta data provider to fetch transcripts via direct PostgreSQL access.

This package includes a REST api (restapi.py) for uta that stands between hgvs and PostgreSQL, along with a data provider for hgvs (utarest.py) that acts as its client.

## Installing the UTA Rest API Locally

Install docker. ***NOTE: Will be under biocommons instead of ccaitlingo later***

    $ docker pull ccaitlingo/uta-rest:uta-rest
    $ docker volume create --name=uta-rest
    $ docker run -p 8000:8000 ccaitlingo/uta-rest:uta-rest

## Using with hgvs

Simply pass the result of utarest's connect() function as an argument into any [hgvs](https://github.com/biocommons/hgvs) tool, e.g. Assembly Mapper.


    >>> import hgvs.dataproviders.utarest
    >>> import hgvs.assemblymapper
    >>> hdp = hgvs.dataproviders.utarest.connect()

    >>> am = hgvs.assemblymapper.AssemblyMapper(hdp,
    ...     assembly_name='GRCh37', alt_aln_method='splign',
    ...     replace_reference=True)
Instead of calling from .uta, you are using .utarest. Both implement the hgvs [data providers interface](https://github.com/biocommons/hgvs/blob/main/src/hgvs/dataproviders/interface.py).

## Using with hgvs (2.0+)

The second version of hgvs allows for selecting a data provider from the options contained in the package utaclients. Uta, uta_rest, and cdot are supported. See [utaclients](https://github.com/ccaitlingo/uta-clients) for more info on each dp.

    >>> import hgvs
    >>> import utaclients
    >>> hdp = utaclients.uta_rest.connect()

    >>> am = hgvs.assemblymapper.AssemblyMapper(hdp,
    ...     assembly_name='GRCh37', alt_aln_method='splign',
    ...     replace_reference=True)

## Developer Installation

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
