# hgvs-dataproviders-rest

Rest interface for [UTA](https://github.com/biocommons/uta) and [SeqRepo](https://github.com/biocommons/biocommons.seqrepo), which combined make up an hgvs data provider.

The uta and seqrepo databases are used by [hgvs](https://github.com/biocommons/hgvs) to perform many of its sequence manipulation functions. The hgvs library includes tools to normalize, validate, and map sequence variants (among other functionalities). In order for hgvs to access info needed for such work, it uses the uta data provider to fetch transcripts and sequences.

This package includes a REST api (restapi.py) for uta that stands between hgvs and uta/seqrepo databases, along with a data provider for hgvs (restclient.py) that acts as its client.

## Installing the Rest Interface Locally

Install docker.

    $ docker pull biocommons/uta-rest:uta-rest
    $ docker volume create --name=uta-rest
    $ docker run -p 8000:8000 biocommons/uta-rest:uta-rest

Or without docker:

    $ make devready
    $ source venv/bin/activate
    $ uvicorn restapi:app

## Using with hgvs

Simply pass the result of utarest's connect() function as an argument into any [hgvs](https://github.com/biocommons/hgvs) tool, e.g. Assembly Mapper.


    >>> import hgvs_dataproviders_rest
    >>> import hgvs.assemblymapper
    >>> hdp = hgvs_dataproviders_rest.connect()

    >>> am = hgvs.assemblymapper.AssemblyMapper(hdp,
    ...     assembly_name='GRCh37', alt_aln_method='splign',
    ...     replace_reference=True)
Instead of calling connect() from hgvs.dataproviders.uta, you are using .hgvs_dataproviders_rest. Both implement the hgvs [data providers interface](https://github.com/biocommons/hgvs/blob/main/src/hgvs/dataproviders/interface.py).

## Using with hgvs (2.0+)

A second version of hgvs is planned, which allows for selecting a data provider out of several supported options: uta, hgvs_dataproviders_rest, cdot, and possibly a future Ensembl interface implementation. See [utaclients](https://github.com/ccaitlingo/uta-clients) for more info on each data provider.

## Developer Installation

    $ make devready
    $ source venv/bin/activate
    $ uvicorn restapi:app --reload
