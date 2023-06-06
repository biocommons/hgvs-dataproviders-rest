import requests
import pytest

# The server you are using to test:
base = "http://127.0.0.1:8000"

@pytest.mark.skip(reason="slow")
def test_seq_e():
    """Exisiting seq."""
    url = base + "/seq/NC_000007.13"
    assert requests.get(url).status_code == 200
    
def test_seq_ne():
    """Nonexisitng seq."""
    url = base + "/seq/fake"
    assert requests.get(url).status_code == 404
    
def test_seq_e_indices():
    """Exisiting seq with start and end indices."""
    url = base + "/seq/NC_000007.13?start_i=10000&end_i=10050"
    assert requests.get(url).status_code == 200

#Exisiting with start
    
#Exisitng with end
    
#Nonexisiting with start and end
    
#Nonexisiting with start
    
#Nonexisiting with end

def test_acs_for_protein_seq_e():
    """Exisiting seq."""
    url = base + "/acs_for_protein_seq/MRAKWRKKRMRRLKRKRRKMRQRSK"
    assert requests.get(url).status_code == 200
 
def test_acs_for_protein_seq_ne():
    """Nonexisiting seq."""
    url = base + "/acs_for_protein_seq/fake"
    assert requests.get(url).status_code == 200 #Should return empty list
    
def test_acs_for_protein_seq_ne_nonalphabetical():
    """Non-alphabetic character seq."""
    url = base + "/acs_for_protein_seq/123"
    assert requests.get(url).status_code == 404
   
def test_gene_info_e():
    """Existing gene."""
    url = base + "/gene_info/VHL"
    assert requests.get(url).status_code == 200

def test_gene_info_ne():
    """Nonexisitng gene."""
    url = base + "/gene_info/VH"
    assert requests.get(url).status_code == 404
    
def test_tx_exons_e():
    """Exisiting seqs."""
    url = base + "/tx_exons/NM_199425.2/NC_000020.10?alt_aln_method=splign"
    assert requests.get(url).status_code == 200
    
def test_tx_exons_ne():
    """Nonexisting seq."""
    url = base + "/tx_exons/NM_199425.2/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    
def test_tx_exons_e_params():
    """Existing seqs with missing param"""
    url = base + "/tx_exons/NM_199425.2/NC_000020.10"
    assert requests.get(url).status_code == 422
    
def test_tx_exons_ne_params():
    """Nonexisting seq with missing param"""
    url = base + "/tx_exons/NM_199425.2/fake"
    assert requests.get(url).status_code == 422 #All 422s check for params before checking if region exists
    
def test_tx_for_gene_e():
    """Existing gene."""
    url = base + "/tx_for_gene/VHL"
    assert requests.get(url).status_code == 200

def test_tx_for_gene_ne():
    """Nonexisitng gene."""
    url = base + "/tx_for_gene/VH"
    assert requests.get(url).status_code == 404
    
def test_tx_for_region_e():
    """Existing region."""
    url = base + "/tx_for_region/NC_000007.13?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 200

def test_tx_for_region_ne():
    """Nonexisting region"""
    url = base + "/tx_for_region/fake?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 200 #Should return empty list
        
def test_tx_region_e_params():
    """Exisiting region with only some params."""
    url = base + "/tx_for_region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    
def test_tx_region_ne_params():
    """Nonexisting region with only some params."""
    url = base + "/tx_for_region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 422 
    
def test_alignments_for_region_e():
    """Existing region."""
    url = base + "/alignments_for_region/NC_000007.13?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 200
    
def test_alignments_for_region_ne():
    """Nonexisting region."""
    url = base + "/alignments_for_region/fake?alt_aln_method=splign&start_i=0&end_i=50"
    assert requests.get(url).status_code == 200 #Empty list 
    
def test_alignmemts_for_region_e_params():
    """Exisiting region with only some params."""
    url = base + "/alignments_for_region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    
def test_alignments_for_region_ne_params():
    """Nonexisting region with only some params."""
    url = base + "/alignments_for_region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    
def test_tx_identity_info_e():
    """Existing transcript."""
    url = base + "/tx_identity_info/NM_199425.2"
    assert requests.get(url).status_code == 200
    
def test_tx_identity_info_ne():
    """Nonexisting transcript."""
    url = base + "/tx_identity_info/fake"
    assert requests.get(url).status_code == 404
    
def test_tx_info_e():
    """Existing seqs."""
    url = base + "/tx_info/NM_199425.2/NC_000020.10?alt_aln_method=splign"
    assert requests.get(url).status_code == 200
    
def test_tx_info_ne():
    """Nonexisting seq."""
    url = base + "/tx_info/NM_199425.2/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    
def test_tx_info_e_param():
    """Existing seqs."""
    url = base + "/tx_info/NM_199425.2/NC_000020.10"
    assert requests.get(url).status_code == 422
    
def test_tx_info_ne_param():
    """Nonexsiting seq."""
    url = base + "/tx_info/NM_199425.2/fake"
    assert requests.get(url).status_code == 422
    
def test_tx_mapping_options_e():
    """Existing transcript."""
    url = base + "/tx_mapping_options/NM_000051.3"
    assert requests.get(url).status_code == 200
    
def test_tx_mapping_options_e_none():
    """Existing transcripts no alignments."""
    url = base + "/tx_mapping_options/NM_..." #Is there an example of a tx_ac with no alginments?
    assert requests.get(url).status_code == 200 #Empty list
    
def test_tx_mapping_options_ne():
    """Nonexisting transcript."""
    url = base + "/tx_mapping_options/fake"
    assert requests.get(url).status_code == 200 #Empty list
    
def test_similar_transcripts_e():
    """Existing transcript."""
    url = base + "/similar_transcripts/NM_000051.3"
    assert requests.get(url).status_code == 200
    
def test_similar_transcripts_e_none():
    """Existing transcripts no similar transcripts."""
    url = base + "/similar_transcripts/NM_..." #Need example
    assert requests.get(url).status_code == 200 #None/null
    
def test_similar_transcripts_ne():
    """Nonexisting transcript."""
    url = base + "/similar_transcripts/fake"
    assert requests.get(url).status_code == 200 #None/null
    
def test_pro_ac_for_tx_ac_e():
    """Existing transcript."""
    url = base + "/pro_ac_for_tx_ac/NM_000051.3"
    assert requests.get(url).status_code == 200
    
def test_pro_ac_for_tx_ac_e_none():
    """Existing transcripts no associated proteins."""
    url = base + "/pro_ac_for_tx_ac/NM_..." #Need example
    assert requests.get(url).status_code == 200 #Empty string
    
def test_pro_ac_for_tx_ac_ne():
    """Nonexisting transcript."""
    url = base + "/pro_ac_for_tx_ac/fake"
    assert requests.get(url).status_code == 200 #None/null
    
def test_assembly_map_e():
    """Existing assembly name."""
    url = base + "/assembly_map/GRCh38.p5"
    assert requests.get(url).status_code == 200
    
def test_assembly_map_ne():
    """Nonexisting assembly name."""
    url = base + "/assembl/gene_info/BRCA1y_map/GROUCH"
    assert requests.get(url).status_code == 404
    