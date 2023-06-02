from hgvs.dataproviders.uta import *
from fastapi import FastAPI, HTTPException
from typing import List  #For optional type hinting in http_422()

app = FastAPI()
conn = connect()

def http_204():
    raise HTTPException(
            status_code=204,
            detail="No content"
        )
    
def http_404(hgvs_exception = None):
    raise HTTPException(
            status_code=404,
            detail= "Not found" if hgvs_exception == None else str(hgvs_exception)
    )
    
def http_422(fields : List[str]):
    raise HTTPException(
            status_code=422,
            detail="Please provide query parameters for the following fields: " + str(fields)
        )
    
def check_valid_ac(ac):
    try:
        conn.get_seq(ac, 0, 1)
        return False
    except HGVSDataNotAvailableError as e: 
        http_404(e)

@app.get("/seq/test")
async def get_tester():
    return {"detail": "test"}

@app.get("/seq/{ac}")
async def seq(ac, start_i: int | None = None, end_i: int | None = None):
    try:
        return conn.get_seq(ac, start_i, end_i)
    except HGVSDataNotAvailableError as e: http_404(e)
     
@app.get("/acs-for-protein-seq/{seq}")
async def acs_for_protein_seq(seq : str):
    acs = conn.get_acs_for_protein_seq(seq)
    return (http_204() if len(acs) == 0 else acs)
    
@app.get("/gene-info/{gene}")
async def gene_info(gene : str):
    gene_info = conn.get_gene_info(gene)
    return (http_404() if gene_info == None else gene_info)

#@app.get("/tx-exons/{tx_ac}/{alt_ac}")
#async def tx_exons(tx_ac, alt_ac, alt_aln_method=None):

@app.get("/tx-for-gene/{gene}")
async def tx_for_gene(gene : str):
    tx = conn.get_tx_for_gene(gene)
    return (http_404() if len(tx) == 0 else tx)

@app.get("/tx-for-region/{alt_ac}")
async def tx_for_region(alt_ac, alt_aln_method=None, start_i=None, end_i=None):
    #Check for valid accession number
    check_valid_ac(alt_ac)
    #Check for blank fields
    params = ["alt_aln_method", "start_i", "end_i"]
    blank_fields = []
    for param in params: 
        if locals()[param] == None: blank_fields.append(param)
    if not len(blank_fields) == 0: http_422(blank_fields)
    #Call uta function
    tx = conn.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)
    return (http_204() if len(tx) == 0 else tx)

@app.get("/alignments-for-region/{alt_ac}", status_code=200)
async def alignments_for_region(alt_ac, start_i: int | None = None, end_i: int | None = None, alt_aln_method=None):
    #Check valid ac
    check_valid_ac(alt_ac)
    #Check fields
    params = ["start_i", "end_i"]
    blank_fields = []
    for param in params: 
        if locals()[param] == None: blank_fields.append(param)
    if not len(blank_fields) == 0: http_422(blank_fields)
    #Call uta function
    alignments = conn.get_alignments_for_region(alt_ac, start_i, end_i, alt_aln_method)
    return (http_204() if len(alignments) == 0 else alignments)

@app.get("/tx-identity-info/{tx_ac}")
async def tx_identity_info(tx_ac):
    try:
        return conn.get_tx_identity_info(tx_ac)
    except HGVSDataNotAvailableError as e: http_404(e)
    
#@app.get("/tx-info/{tx_ac}/{alt_ac}")
#async def tx_info(tx_ac, alt_ac, alt_aln_method=None):

@app.get("/tx-mapping-options/{tx_ac}")
async def tx_mapping_options(tx_ac):
    check_valid_ac(tx_ac)
    rows = conn.get_tx_mapping_options(tx_ac)
    return (http_204() if len(rows) == 0 else rows)

@app.get("/similar-transcripts/{tx_ac}")
async def similar_transcripts(tx_ac):
    check_valid_ac(tx_ac)
    rows = conn.get_similar_transcripts(tx_ac)
    return (http_204() if len(rows) == 0 else rows)

@app.get("/pro-ac-for-tx-ac/{tx_ac}")
async def pro_ac_for_tx_ac(tx_ac):
    check_valid_ac(tx_ac)
    protein_ac = conn.get_pro_ac_for_tx_ac(tx_ac)
    return (http_204() if protein_ac == None else protein_ac)

@app.get("/assembly-map/{assembly_name}")
async def assmbly_map(assembly_name):
    return conn.get_assembly_map(assembly_name)

