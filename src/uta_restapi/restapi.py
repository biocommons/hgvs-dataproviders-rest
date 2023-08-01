import datetime
from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException
from hgvs.dataproviders.uta import UTABase, connect
from hgvs.exceptions import HGVSDataNotAvailableError, HGVSError
from pydantic import BaseModel

app = FastAPI()
conn = connect()


def http_404(hgvs_exception=None):
    raise HTTPException(status_code=404, detail="Not found" if not hgvs_exception else str(hgvs_exception))


class Gene(BaseModel):
    hgnc: str
    maploc: str
    descr: str
    summary: str
    aliases: str
    added: datetime.datetime


class Transcript_Exon(BaseModel):
    hgnc: str
    tx_ac: str
    alt_ac: str
    alt_aln_method: str
    alt_strand: int
    ord: int
    tx_start_i: int
    tx_end_i: int
    alt_start_i: int
    alt_end_i: int
    cigar: str
    tx_aseq: None  # Out of 5595819 rows in the tx_exon_aln_v table, this is always null/None
    alt_aseq: None  # Same
    tes_exon_set_id: int
    aes_exon_set_id: int
    tx_exon_id: int
    alt_exon_id: int
    exon_aln_id: int


class Transcript(BaseModel):
    hgnc: str
    cds_start_i: int
    cds_end_i: int
    tx_ac: str
    alt_ac: str
    alt_aln_method: str
    lengths: Optional[List[int]]


class Similar_Transcript(BaseModel):
    tx_ac1: str
    tx_ac2: str
    hgnc_eq: bool
    cds_eq: Optional[bool]
    es_fp_eq: bool
    cds_es_fp_eq: Optional[bool]
    cds_exon_lengths_fp_eq: Optional[bool]


class Alignment_Set(BaseModel):
    tx_ac: str
    alt_ac: str
    alt_aln_method: str


@app.get("/ping")
async def ping() -> dict:
    """returns the data_version, schema_version, and sequence_source from uta."""
    d = {}
    d["data_version"] = conn.data_version()
    d["schema_version"] = conn.schema_version()
    d["sequence_source"] = UTABase.sequence_source()
    return d


@app.get("/seq/{ac}")
async def seq(ac: str, start_i: Optional[int] = None, end_i: Optional[int] = None) -> str:
    """
    calls get_seq from utarest.py
    raises an error if the accession number is not found in the database.
    """
    try:
        return conn.get_seq(ac, start_i, end_i)
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/acs_for_protein_seq/{seq}")
async def acs_for_protein_seq(seq: str) -> List:
    """
    calls get_acs_for_protein_seq from utarest.py
    raises an error if the sequence is not found in the database.
    """
    try:
        return conn.get_acs_for_protein_seq(seq)
    except RuntimeError as e:
        http_404(e)


@app.get("/gene_info/{gene}")
async def gene_info(gene: str) -> Union[dict, None]:
    """
    calls get_gene_info from utarest.py
    returns information as a Gene model or None.
    """
    gene = conn.get_gene_info(gene)
    return gene if gene is None else dict(gene)


@app.get("/tx_exons/{tx_ac}/{alt_ac}")
async def tx_exons(tx_ac: str, alt_ac: str, alt_aln_method: str) -> List:
    """
    calls get_tx_exons from utarest.py
    raises an error if no transcript exons are found for the given accessions and alignment method.
    otherwise returns information as a list of Transcript models.
    """
    try:
        rows = conn.get_tx_exons(tx_ac, alt_ac, alt_aln_method)
        if not rows:
            return rows
        # Convert DictRow to dict to preserve dictionary
        t_exons = []
        for r in rows:
            t_exons.append(dict(r))
        return t_exons
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/tx_for_gene/{gene}")
async def tx_for_gene(gene: str) -> Union[List, None]:
    """calls get_tx_for_gene from utarest.py"""
    rows = conn.get_tx_for_gene(gene)
    if not rows:
        return rows
    # Convert DictRow to dict to preserve dictionary
    transcripts = []
    for r in rows:
        transcripts.append(dict(r))
    return transcripts


@app.get("/tx_for_region/{alt_ac}")
async def tx_for_region(alt_ac: str, alt_aln_method: str, start_i: int, end_i: int) -> Union[List, None]:
    """calls get_tx_for_region from utarest.py"""
    rows = conn.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)
    if not rows:
        return rows
    # Convert DictRow to dict to preserve dictionary
    transcripts = []
    for r in rows:
        transcripts.append(dict(r))
    return transcripts


@app.get("/alignments_for_region/{alt_ac}", status_code=200)
async def alignments_for_region(alt_ac: str, start_i: int, end_i: int, alt_aln_method: Optional[str] = None) -> List:
    """calls get_alignments_for_region from utarest.py"""
    return conn.get_alignments_for_region(alt_ac, start_i, end_i, alt_aln_method)


@app.get("/tx_identity_info/{tx_ac}")
async def tx_identity_info(tx_ac: str) -> dict:
    """
    calls get_tx_identity_info from utarest.py
    raises an error if the transcript acession is not found in the database.
    otherwise returns information as a Transcript model.
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
    otherwise returns information as a Transcript model.
    """
    try:
        return dict(conn.get_tx_info(tx_ac, alt_ac, alt_aln_method))
    except HGVSDataNotAvailableError as e:
        http_404(e)
    except HGVSError as e:
        http_404(e)


@app.get("/tx_mapping_options/{tx_ac}")
async def tx_mapping_options(tx_ac: str) -> Union[List, None]:
    """
    calls get_tx_mapping_options from utarest.py
    returns information as a list of Alignment_Set models or None.
    """
    rows = conn.get_tx_mapping_options(tx_ac)
    if not rows:
        return rows
    # Convert DictRow to dict to preserve dictionary
    mapping_options = []
    for r in rows:
        mapping_options.append(dict(r))
    return mapping_options


@app.get("/similar_transcripts/{tx_ac}")
async def similar_transcripts(tx_ac: str) -> Union[List, None]:
    """
    calls get_similar_transcripts from utarest.py
    returns information as a list of Similar_Transcript models or None.
    """
    rows = conn.get_similar_transcripts(tx_ac)
    if not rows:
        return rows
    # Convert DictRow to dict to preserve dictionary
    transcripts = []
    for r in rows:
        transcripts.append(dict(r))
    return transcripts


@app.get("/pro_ac_for_tx_ac/{tx_ac}")
async def pro_ac_for_tx_ac(tx_ac: str) -> Union[str, None]:
    """calls get_pro_ac_for_tx_ac from utarest.py"""
    return conn.get_pro_ac_for_tx_ac(tx_ac)


@app.get("/assembly_map/{assembly_name}")
async def assembly_map(assembly_name: str) -> dict:
    """
    calls get_assembly_map from utarest.py
    raises an error if not given an exisiting assembly map name
    """
    try:
        return conn.get_assembly_map(assembly_name)
    except Exception as e:
        http_404(e)
