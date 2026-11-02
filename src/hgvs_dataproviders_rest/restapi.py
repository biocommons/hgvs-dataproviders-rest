from fastapi import FastAPI, HTTPException
from hgvs.dataproviders.uta import UTABase, connect
from hgvs.exceptions import HGVSDataNotAvailableError, HGVSError

app = FastAPI()
conn = connect()


def http_404(hgvs_exception=None):
    raise HTTPException(
        status_code=404, detail="Not found" if not hgvs_exception else str(hgvs_exception)
    )


@app.get("/ping")
async def ping() -> dict:
    """returns the data_version, schema_version, and sequence_source from uta."""
    d = {}
    d["data_version"] = conn.data_version()
    d["schema_version"] = conn.schema_version()
    d["sequence_source"] = UTABase.sequence_source()
    return d


@app.get("/seq/{ac}")
async def seq(ac: str, start_i: int | None = None, end_i: int | None = None) -> str:
    """
    calls get_seq from utarest.py
    raises an error if the accession number is not found in the database.
    """
    try:
        return conn.get_seq(ac, start_i, end_i)
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/acs_for_protein_seq/{seq}")
async def acs_for_protein_seq(seq: str) -> list:
    """
    calls get_acs_for_protein_seq from utarest.py
    raises an error if the sequence is not found in the database.
    """
    try:
        return conn.get_acs_for_protein_seq(seq)
    except RuntimeError as e:
        http_404(e)


@app.get("/gene_info/{gene}")
async def gene_info(gene: str) -> dict | None:
    """calls get_gene_info from utarest.py."""
    gene = conn.get_gene_info(gene)
    return gene if gene is None else dict(gene)


@app.get("/tx_exons/{tx_ac}/{alt_ac}")
async def tx_exons(tx_ac: str, alt_ac: str, alt_aln_method: str) -> list:
    """
    calls get_tx_exons from utarest.py
    raises an error if no transcript exons are found for the given accessions and alignment method.
    otherwise returns information as a list of dictionaries.
    """
    try:
        rows = conn.get_tx_exons(tx_ac, alt_ac, alt_aln_method)
    except HGVSDataNotAvailableError as e:
        http_404(e)
    else:
        return [dict(row) for row in rows] if rows else rows


@app.get("/tx_for_gene/{gene}")
async def tx_for_gene(gene: str) -> list | None:
    """calls get_tx_for_gene from utarest.py"""
    rows = conn.get_tx_for_gene(gene)
    return [dict(row) for row in rows] if rows else rows


@app.get("/tx_for_region/{alt_ac}")
async def tx_for_region(alt_ac: str, alt_aln_method: str, start_i: int, end_i: int) -> list | None:
    """calls get_tx_for_region from utarest.py"""
    rows = conn.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)
    return [dict(row) for row in rows] if rows else rows


@app.get("/alignments_for_region/{alt_ac}", status_code=200)
async def alignments_for_region(
    alt_ac: str, start_i: int, end_i: int, alt_aln_method: str | None = None
) -> list:
    """calls get_alignments_for_region from utarest.py"""
    return conn.get_alignments_for_region(alt_ac, start_i, end_i, alt_aln_method)


@app.get("/tx_identity_info/{tx_ac}")
async def tx_identity_info(tx_ac: str) -> dict:
    """
    calls get_tx_identity_info from utarest.py
    raises an error if the transcript acession is not found in the database.
    otherwise returns information as a dictionary.
    """
    try:
        return dict(conn.get_tx_identity_info(tx_ac))
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/tx_info/{tx_ac}/{alt_ac}")
async def tx_info(tx_ac: str, alt_ac: str, alt_aln_method: str) -> dict:
    """
    calls get_tx_info from utarest.py
    raises an error if no transcripts are found for the given accessions and alignment method, or if uta recieves more than one transcript when fetching.
    otherwise returns information as a dictionary.
    """
    try:
        return dict(conn.get_tx_info(tx_ac, alt_ac, alt_aln_method))
    except HGVSDataNotAvailableError as e:
        http_404(e)
    except HGVSError as e:
        http_404(e)


@app.get("/tx_mapping_options/{tx_ac}")
async def tx_mapping_options(tx_ac: str) -> list | None:
    """calls get_tx_mapping_options from utarest.py."""
    rows = conn.get_tx_mapping_options(tx_ac)
    return [dict(row) for row in rows] if rows else rows


@app.get("/similar_transcripts/{tx_ac}")
async def similar_transcripts(tx_ac: str) -> list | None:
    """calls get_similar_transcripts from utarest.py."""
    rows = conn.get_similar_transcripts(tx_ac)
    return [dict(row) for row in rows] if rows else rows


@app.get("/pro_ac_for_tx_ac/{tx_ac}")
async def pro_ac_for_tx_ac(tx_ac: str) -> str | None:
    """calls get_pro_ac_for_tx_ac from utarest.py"""
    return conn.get_pro_ac_for_tx_ac(tx_ac)


@app.get("/assembly_map/{assembly_name}")
async def assembly_map(assembly_name: str) -> dict:
    """
    calls get_assembly_map from utarest.py
    raises an error if not given an exisiting assembly map name.
    """
    try:
        return conn.get_assembly_map(assembly_name)
    except Exception as e:
        http_404(e)
