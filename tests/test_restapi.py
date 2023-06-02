import requests
import pytest

# The server you are using to test:
base = "http://127.0.0.1:8000"

@pytest.mark.skip(reason="slow")
def test_seq():
    #Exisiting seq
    url = base + "/seq/NC_000007.13"
    assert requests.get(url).status_code == 200
    
    #Nonexisitng seq
    url = base + "/seq/fake"
    assert requests.get(url).status_code == 404
    
    #Exisiting seq with start and end indices
    url = base + "/seq/NC_000007.13?start_i=10000&end_i=10050"
    assert requests.get(url).status_code == 200
    
    #Exisiting with start
    
    #Exisitng with end
    
    #Nonexisiting with start and end
    
    #Nonexisiting with start
    
    #Nonexisitng with end

def test_acs_for_protein_seq():
    # Is there an ac that is associated with a short sequence?
    # Or would there be another better way to write this test?
    
    """
    #Exisiting seq
    seq_from_ac = requests.get("http://127.0.0.1:8000/seq/NC_000007.13").text
    url = base + "/acs-for-protein-seq/" + seq_from_ac
    assert "NC_000007.13" == requests.get(url).text
    assert requests.get(url).status_code == 200
    
    #Nonexisiting seq
    url = base + "/acs-for-protein/fake"
    assert requests.get(url).statuscode == 204
    """
   
def test_gene_info():
    #Existing gene
    url = base + "/gene-info/VHL"
    assert requests.get(url).status_code == 200
    
    #Nonexisitng gene
    url = base + "/gene-info/VH"
    assert requests.get(url).status_code == 404
    
print(requests.get(base + "/gene-info/VH").reason)
    
def test_tx_for_gene():
    #Existing gene
    url = base + "/tx-for-gene/VHL"
    assert requests.get(url).status_code == 200
    
    #Nonexisitng gene
    url = base + "/tx-for-gene/VH"
    assert requests.get(url).status_code == 404
    
def test_tx_for_region():
    #Existing region
    url = base + "/tx-for-region/NC_000007.13?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 204
    
    #Nonexisting region
    url = base + "/tx-for-region/fake?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 404
    
    #Exisiting region with some params
    url = base + "/tx-for-region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    
    #Nonexisting region wtih some params
    url = base + "/tx-for-region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    
def test_alignments_for_region():
    #Existing region
    url = base + "/alignments-for-region/NC_000007.13?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 204
    
    #Nonexisting region
    url = base + "/alignments-for-region/fake?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 404
    
    #Exisiting region with some params
    url = base + "/alignments-for-region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    
    #Nonexisting region wtih some params
    url = base + "/alignments-for-region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    
def test_tx_identity_info():
    #Existing transcript
    url = base + "/tx-identity-info/NM_199425.2"
    assert requests.get(url).status_code == 200
    
    #Nonexisting transcript
    url = base + "/tx-identity-info/fake"
    assert requests.get(url).status_code == 404
    
def test_tx_mapping_options():
    #Existing transcript
    url = base + "/tx-mapping-options/NM_000051.3"
    assert requests.get(url).status_code == 200
    
    #Existing transcripts no alignments
    url = base + "/tx-mapping-options/NC_000007.13"
    assert requests.get(url).status_code == 204
    
    #Nonexisting transcript
    url = base + "/tx-mapping-options/fake"
    assert requests.get(url).status_code == 404
    
def test_similar_transcripts():
    #Existing transcript
    url = base + "/similar-transcripts/NM_000051.3"
    assert requests.get(url).status_code == 200
    
    #Existing transcripts no similar transcripts
    url = base + "/similar-transcripts/NC_000007.13"
    assert requests.get(url).status_code == 204
    
    #Nonexisting transcript
    url = base + "/similar-transcripts/fake"
    assert requests.get(url).status_code == 404
    
def test_pro_ac_for_tx_ac():
    #Existing transcript
    url = base + "/pro-ac-for-tx-ac/NM_000051.3"
    assert requests.get(url).status_code == 200
    
    #Existing transcripts no associated proteins
    url = base + "/pro-ac-for-tx-ac/NC_000007.13"
    assert requests.get(url).status_code == 204
    
    #Nonexisting transcript
    url = base + "/pro-ac-for-tx-ac/fake"
    assert requests.get(url).status_code == 404
    
def test_assembly_map():
    url = base + "/assembly-map/GRCh38.p5"
    assert requests.get(url).status_code == 200