from hgvs.dataproviders.uta import *
from fastapi import FastAPI, HTTPException
from typing import List  #For optional type hinting

app = FastAPI()
conn = connect()

def http_404(hgvs_exception = None):
    raise HTTPException(
            status_code=404,
            detail="Not found" if hgvs_exception == None else str(hgvs_exception)
    )
    
def http_422(fields : List[str]):
    raise HTTPException(
            status_code=422,
            detail="Please provide query parameters for the following fields: " + str(fields)
        )
    
def check_valid_ac(ac):
    try:
        conn.get_seq(ac, 0, 1)
        return
    except HGVSDataNotAvailableError as e: 
        http_404(e)

@app.get("/seq/{ac}")
async def seq(ac : str, start_i: int | None = None, end_i: int | None = None) -> str:
    try:
        return conn.get_seq(ac, start_i, end_i)
    except HGVSDataNotAvailableError as e: http_404(e)
     
@app.get("/acs_for_protein_seq/{seq}")
async def acs_for_protein_seq(seq : str) -> List | None:
    try:
        acs = conn.get_acs_for_protein_seq(seq)
    except RuntimeError as e: http_404(e)
    
@app.get("/gene_info/{gene}")
async def gene_info(gene : str) -> List:
    gene_info = conn.get_gene_info(gene)
    return (http_404() if gene_info == None else gene_info)

@app.get("/tx_exons/{tx_ac}/{alt_ac}")
async def tx_exons(tx_ac : str, alt_ac : str, alt_aln_method: str | None) -> List[List]:
    if alt_aln_method == None: http_422(["alt_aln_method"])
    try:
        rows = conn.get_tx_exons(tx_ac, alt_ac, alt_aln_method)
        return (http_404("No transcript exon info for supplied accession") if rows == None else rows)
    except HGVSDataNotAvailableError as e: http_404(e)

@app.get("/tx_for_gene/{gene}")
async def tx_for_gene(gene : str) -> List[List]:
    tx = conn.get_tx_for_gene(gene)
    return (http_404() if len(tx) == 0 else tx)

@app.get("/tx_for_region/{alt_ac}")
async def tx_for_region(alt_ac : str, alt_aln_method : str, start_i : int, end_i : int) -> List[List]: #dict?
    #Check for blank fields
    params = ["alt_aln_method", "start_i", "end_i"]
    blank_fields = []
    for param in params: 
        if locals()[param] == None: blank_fields.append(param)
    if not len(blank_fields) == 0: http_422(blank_fields)
    #Call uta function
    return conn.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)

@app.get("/alignments_for_region/{alt_ac}", status_code=200)
async def alignments_for_region(alt_ac, start_i: int | None, end_i: int | None, alt_aln_method : str | None) -> List[List]: #dict?
    #Check fields
    params = ["start_i", "end_i"]
    blank_fields = []
    for param in params: 
        if locals()[param] == None: blank_fields.append(param)
    if not len(blank_fields) == 0: http_422(blank_fields)
    #Call uta function
    return conn.get_alignments_for_region(alt_ac, start_i, end_i, alt_aln_method)

@app.get("/tx_identity_info/{tx_ac}")
async def tx_identity_info(tx_ac : str) -> List:
    try:
        return conn.get_tx_identity_info(tx_ac)
    except HGVSDataNotAvailableError as e: http_404(e)

@app.get("/tx_info/{tx_ac}/{alt_ac}")
async def tx_info(tx_ac : str, alt_ac : str, alt_aln_method : str | None) -> List:
    if alt_aln_method == None: http_422(["alt_aln_method"])
    try:
        rows = conn.get_tx_info(tx_ac, alt_ac, alt_aln_method)
        return (http_404("No transcript exon info for supplied accession") if rows == None else rows)
    except HGVSDataNotAvailableError as e: http_404(e)
    except HGVSError as e: http_404(e)

@app.get("/tx_mapping_options/{tx_ac}")
async def tx_mapping_options(tx_ac : str) -> List[List]:
    return conn.get_tx_mapping_options(tx_ac)

@app.get("/similar_transcripts/{tx_ac}")
async def similar_transcripts(tx_ac : str) -> List[List]:
    return conn.get_similar_transcripts(tx_ac)

@app.get("/pro_ac_for_tx_ac/{tx_ac}")
async def pro_ac_for_tx_ac(tx_ac : str) -> str | None:
    return conn.get_pro_ac_for_tx_ac(tx_ac)

@app.get("/assembly_map/{assembly_name}")
async def assmbly_map(assembly_name : str) -> dict:
    try:
        return conn.get_assembly_map(assembly_name)
    except Exception as e: http_404(e)

