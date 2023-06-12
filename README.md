# uta-rest

Rest interface for [UTA](https://github.com/biocommons/uta) 

 ## Installing the UTA Rest API Locally

Install docker.

    $ docker pull biocommons/uta-rest:uta-rest
    $ docker volume create --name=uta-rest
    $ docker run -p 8000:8000 biocommons/uta-rest:uta-rest

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