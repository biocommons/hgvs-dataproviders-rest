import hgvs
import logging
import os

def connect(db_url=None, pooling=hgvs.global_config.uta.pooling, application_name=None, mode=None, cache=None):
    """Connect to a UTA database instance and return a UTA interface instance.

    :param db_url: URL for database connection
    :type db_url: string
    :param pooling: whether to use connection pooling (postgresql only)
    :type pooling: bool
    :param application_name: log application name in connection (useful for debugging; PostgreSQL only)
    :type application_name: str
    
    When called with an explicit db_url argument, that db_url is used for connecting.

    When called without an explicit argument, the function default is
    determined by the environment variable UTA_DB_URL if it exists, or
    hgvs.datainterface.uta.public_db_url otherwise.
    
    >>> hdp = connect()
    >>> hdp.schema_version()
    '1.1'
    
    The format of the db_url is driver://user:pass@host/database/schema (the same
    as that used by SQLAlchemy).  Examples:

    A remote public postgresql database:
        postgresql://anonymous:anonymous@uta.biocommons.org/uta/uta_20170707'

    A local postgresql database:
        postgresql://localhost/uta_dev/uta_20170707

    For postgresql db_urls, pooling=True causes connect to use a
    psycopg2.pool.ThreadedConnectionPool.
    
    """
    
    logger = logging.getLogger(__name__)
    logger.debug("connecting to " + str(db_url) + "...")

    if db_url is None:
        # Default as utarest?
        db_url = os.environ.get("UTAREST_URL", "https://api.biocommons.org/utarest/0")
        # Default as uta?
        # db_url = uta._get_uta_db_url()
        
    if "PYTEST_CURRENT_TEST" in os.environ and "localhost" not in db_url:
        logger.warning(f"You are executing tests using remote data ({db_url})")
        
        
    # Supported: postgresql, sqlite, cdot, and utarest
    if db_url.startswith("postgresql"):
        import hgvs.dataproviders.uta as uta
        url = uta._parse_url(db_url)
        if url.scheme == "sqlite":
            conn = uta.UTA_sqlite(url, mode, cache)
        if url.scheme == "postgresql":
            conn = uta.UTA_postgresql(url=url, pooling=pooling, application_name=application_name, mode=mode, cache=cache)
        else:
            raise RuntimeError("{url.scheme} in {url} is not currently supported".format(url=url))   
    elif db_url.startswith("http"):
        if db_url.__contains__("cdot"):
            # cdot at either https://cdot.cc or http://cdot.cc
            import cdot.cdot.hgvs.dataproviders.json_data_provider as cdot
            conn = cdot.RESTDataProvider(url)
        else:
            import uta_restapi
            conn = uta_restapi.UTAREST(url)
    else:
        raise RuntimeError("{url} is not currently supported".format(url=url))
    
    
    logger.info("connected to " + str(db_url) + "...")
    return conn
        
    