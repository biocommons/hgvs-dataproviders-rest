import datetime
from typing import List, Optional, Union  # For optional type hinting

from fastapi import FastAPI, HTTPException
from hgvs.dataproviders.uta import UTABase, connect
from hgvs.exceptions import HGVSDataNotAvailableError, HGVSError
from pydantic import BaseModel

app = FastAPI()
conn = connect()


def http_404(hgvs_exception=None):
    raise HTTPException(status_code=404, detail="Not found" if not hgvs_exception else str(hgvs_exception))


def check_valid_ac(ac): 
    try:
        conn.get_seq(ac, 0, 1)
        return
    except HGVSDataNotAvailableError as e:
        http_404(e)


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


# ping endpoint -> return data, schema, sequence version in json
@app.get("/ping")
async def ping() -> dict:
    d = {}
    d["data_version"] = conn.data_version()
    d["schema_version"] = conn.schema_version()
    d["sequence_source"] = UTABase.sequence_source()
    return d


@app.get("/seq/{ac}")
async def seq(ac: str, start_i: Optional[int] = None, end_i: Optional[int] = None) -> str:
    try:
        return conn.get_seq(ac, start_i, end_i)
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/acs_for_protein_seq/{seq}")
async def acs_for_protein_seq(seq: str) -> List:
    try:
        return conn.get_acs_for_protein_seq(seq)
    except RuntimeError as e:
        http_404(e)


@app.get("/gene_info/{gene}", response_model=Optional[Gene])
async def gene_info(gene: str):
    r = conn.get_gene_info(gene)
    return r if not r else Gene(hgnc=r[0], maploc=r[1], descr=r[2], summary=r[3], aliases=r[4], added=r[5])


@app.get("/tx_exons/{tx_ac}/{alt_ac}", response_model=List[Transcript_Exon])
async def tx_exons(tx_ac: str, alt_ac: str, alt_aln_method: str):
    try:
        rows = conn.get_tx_exons(tx_ac, alt_ac, alt_aln_method)
        if not rows:
            return rows
        # Make a list of Transcript_Exon objects
        tx_exons = []
        for exon in rows:
            tx_exons.append(
                Transcript_Exon(
                    hgnc=exon[0],
                    tx_ac=exon[1],
                    alt_ac=exon[2],
                    alt_aln_method=exon[3],
                    alt_strand=exon[4],
                    ord=exon[5],
                    tx_start_i=exon[6],
                    tx_end_i=exon[7],
                    alt_start_i=exon[8],
                    alt_end_i=exon[9],
                    cigar=exon[10],
                    tx_aseq=exon[11],
                    alt_aseq=exon[12],
                    tes_exon_set_id=exon[13],
                    aes_exon_set_id=exon[14],
                    tx_exon_id=exon[15],
                    alt_exon_id=exon[16],
                    exon_aln_id=exon[17],
                )
            )
        return tx_exons
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/tx_for_gene/{gene}")
async def tx_for_gene(gene: str) -> List:
    tx = conn.get_tx_for_gene(gene)
    return tx


@app.get("/tx_for_region/{alt_ac}")
async def tx_for_region(alt_ac: str, alt_aln_method: str, start_i: int, end_i: int) -> List:
    return conn.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)


@app.get("/alignments_for_region/{alt_ac}", status_code=200)
async def alignments_for_region(alt_ac, start_i: int, end_i: int, alt_aln_method: Optional[str] = None) -> List:
    return conn.get_alignments_for_region(alt_ac, start_i, end_i, alt_aln_method)


@app.get("/tx_identity_info/{tx_ac}", response_model=Transcript)
async def tx_identity_info(tx_ac: str):
    try:
        r = conn.get_tx_identity_info(tx_ac)
        return Transcript(
            tx_ac=r[0], alt_ac=r[1], alt_aln_method=r[2], cds_start_i=r[3], cds_end_i=r[4], lengths=r[5], hgnc=r[6]
        )
    except HGVSDataNotAvailableError as e:
        http_404(e)


@app.get("/tx_info/{tx_ac}/{alt_ac}", response_model=Transcript, response_model_exclude_unset=True)
async def tx_info(tx_ac: str, alt_ac: str, alt_aln_method: str):
    try:
        r = conn.get_tx_info(tx_ac, alt_ac, alt_aln_method)
        return Transcript(hgnc=r[0], cds_start_i=r[1], cds_end_i=r[2], tx_ac=r[3], alt_ac=r[4], alt_aln_method=r[5])

    except HGVSDataNotAvailableError as e:
        http_404(e)
    except HGVSError as e:
        http_404(e)


@app.get("/tx_mapping_options/{tx_ac}", response_model=List[Alignment_Set])
async def tx_mapping_options(tx_ac: str):
    rows = conn.get_tx_mapping_options(tx_ac)
    if not rows:
        return rows
    # Make a list of Alignment_Set objects
    alignments = []
    for align in rows:
        alignments.append(Alignment_Set(tx_ac=align[0], alt_ac=align[1], alt_aln_method=align[2]))
    return alignments


@app.get("/similar_transcripts/{tx_ac}", response_model=List[Similar_Transcript])
async def similar_transcripts(tx_ac: str):
    rows = conn.get_similar_transcripts(tx_ac)
    if not rows:
        return rows
    # Make a list of Transcript objects
    transcripts = []
    for ts in rows:
        transcripts.append(
            Similar_Transcript(
                tx_ac1=ts[0],
                tx_ac2=ts[1],
                hgnc_eq=ts[2],
                cds_eq=ts[3],
                es_fp_eq=ts[4],
                cds_es_fp_eq=ts[5],
                cds_exon_lengths_fp_eq=ts[6],
            )
        )
    return transcripts


@app.get("/pro_ac_for_tx_ac/{tx_ac}")
async def pro_ac_for_tx_ac(tx_ac: str) -> Union[str, None]:
    return conn.get_pro_ac_for_tx_ac(tx_ac)


@app.get("/assembly_map/{assembly_name}")
async def assmbly_map(assembly_name: str) -> dict:
    try:
        return conn.get_assembly_map(assembly_name)
    except Exception as e:
        http_404(e)
