import src.uta_restapi.utarest as utarest
import datetime
import hgvs.dataproviders.uta as uta
import pytest

conn_uta = uta.connect()
conn_utarest = utarest.connect()

def just_values(dictionaries: list[dict]) -> list[list]:
    """Like the opposite of dict(), when dict() can't be used.
    (i.e. to compare just the values of a dictionary against a list of values)"""
    newlist = []
    for dictionary in dictionaries:
        newlist.append(list(dictionary.values()))
    return newlist

def equal_regardless_of_order(list, other):
    """To compare lists that are neither hashable or stortable."""
    for item in list:
        try:
            other.remove(item)
        except ValueError:
            return False
    return True
        
#########################################################################
# u = UTA
# r = UTA Rest
        
@pytest.mark.skip(reason="super slow")
def test_seq_e():
    """Existing seq."""
    u = conn_uta.get_seq("NC_000007.13")
    r = conn_utarest.get_seq("NC_000007.13").json()
    assert u == r
    
def test_seq_ne():
    """Nonexisting seq."""
    r = conn_utarest.get_seq("fake")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn_uta.get_seq("fake")
        
@pytest.mark.skip(reason="just not fast")
def test_seq_e_indices():
    """Existing seq with start and end indices."""
    u = conn_uta.get_seq("NC_000007.13", 10000, 10050)
    r = conn_utarest.get_seq("NC_000007.13", 10000, 10050).json()
    assert u == r

def test_acs_for_protein_seq_e():
    """Existing seq."""
    u = conn_uta.get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK")
    r = conn_utarest.get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK").json()
    assert u == r
    
def test_acs_for_protein_seq_ne():
    """Nonexisting seq."""
    u = conn_uta.get_acs_for_protein_seq("fake")
    r = conn_utarest.get_acs_for_protein_seq("fake").json()
    assert u == r
    
def test_acs_for_protein_seq_ne_nonalphabetical():
    """Non-alphabetic character seq."""
    r = conn_utarest.get_acs_for_protein_seq("123")
    assert r.status_code == 404
    with pytest.raises(RuntimeError):
        conn_uta.get_acs_for_protein_seq("123")
        
def test_gene_info_e():
    """Existing gene."""
    u = dict(conn_uta.get_gene_info("VHL"))
    r = conn_utarest.get_gene_info("VHL").json()
    r["added"] = datetime.datetime.fromisoformat(r["added"])
    assert u == r
    
def test_gene_info_ne():
    """Nonexistng gene."""
    u = conn_uta.get_gene_info("VH")
    r = conn_utarest.get_gene_info("VH").json()
    assert u == r
        
def test_tx_exons_e():
    """Existing seqs."""
    u = conn_uta.get_tx_exons("NM_199425.2", "NC_000020.10", "splign")
    r = just_values(conn_utarest.get_tx_exons("NM_199425.2", "NC_000020.10", "splign").json())
    assert u == r
    
def test_tx_exons_ne():
    """Nonexisting seq."""
    r = conn_utarest.get_tx_exons("NM_199425.2", "fake", "splign")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn_uta.get_tx_exons("NM_199425.2", "fake", "splign")
        
def test_tx_exons_e_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        conn_utarest.get_tx_exons("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        conn_uta.get_tx_exons("NM_199425.2", "NC_000020.10")
        
def test_tx_exons_ne_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        conn_utarest.get_tx_exons("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        conn_uta.get_tx_exons("NM_199425.2", "fake")
        
def test_tx_for_gene_e():
    """Existing gene."""
    u = conn_uta.get_tx_for_gene("VHL")
    r = conn_utarest.get_tx_for_gene("VHL").json()
    assert equal_regardless_of_order(u, r)
    
def test_tx_for_gene_ne():
    """Nonexisitng gene."""
    u = conn_uta.get_tx_for_gene("VH")
    r = conn_utarest.get_tx_for_gene("VH").json()
    assert u == r
    
def test_tx_for_region_e(): # Need example
    """Existing region."""
    u = conn_uta.get_tx_for_region("NC_000007.13", "splign", 0, 50)
    r = conn_utarest.get_tx_for_region("NC_000007.13", "splign", 0, 50).json()
    assert u == r
    
def test_tx_for_region_ne():
    """Nonexisting region"""
    u = conn_uta.get_tx_for_region("fake", "splign", 0, 50)
    r = conn_utarest.get_tx_for_region("fake", "splign", 0, 50).json()
    assert u == r
    
def test_tx_for_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        conn_utarest.get_tx_for_region("NC_000007.13", "splign")
    with pytest.raises(TypeError):
        conn_uta.get_tx_for_region("NC_000007.13", "splign")
        
def test_tx_for_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        conn_utarest.get_tx_for_region("fake", "splign")
    with pytest.raises(TypeError):
        conn_uta.get_tx_for_region("fake", "splign")
    
def test_alignments_for_region_e(): # Need example
    """Existing region."""
    u = conn_uta.get_alignments_for_region("NC_000007.13", 0, 50)
    r = conn_utarest.get_alignments_for_region("NC_000007.13", 0, 50).json()
    assert u == r
    
def test_alignments_for_region_ne():
    """Nonexisting region"""
    u = conn_uta.get_alignments_for_region("fake", 0, 50)
    r = conn_utarest.get_alignments_for_region("fake", 0, 50).json()
    assert u == r
    
def test_alignments_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        conn_utarest.get_alignments_for_region("NC_000007.13")
    with pytest.raises(TypeError):
        conn_uta.get_alignments_for_region("NC_000007.13")
        
def test_alignments_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        conn_utarest.get_alignments_for_region("fake")
    with pytest.raises(TypeError):
        conn_uta.get_alignments_for_region("fake")
    
def test_tx_identity_info_e():
    """Existing transcript."""
    u = dict(conn_uta.get_tx_identity_info("NM_199425.2"))
    r = conn_utarest.get_tx_identity_info("NM_199425.2").json()
    assert u == r
    
def test_tx_identity_info_ne():
    """Nonexisting transcript."""
    r = conn_utarest.get_tx_identity_info("fake")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn_uta.get_tx_identity_info("fake")
        
def test_tx_info_e(): # Check with Reece
    """Existing seqs."""
    u = dict(conn_uta.get_tx_info("NM_199425.2", "NC_000020.10", "splign"))
    u["lengths"] = None
    r = conn_utarest.get_tx_info("NM_199425.2", "NC_000020.10", "splign").json()
    assert u == r
    
def test_tx_info_ne():
    """Nonexisting seq."""
    r = conn_utarest.get_tx_info("NM_199425.2", "fake", "splign")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn_uta.get_tx_info("NM_199425.2", "fake", "splign")
        
def test_tx_info_e_param():
    """Existing seqs."""
    with pytest.raises(TypeError):
        conn_utarest.get_tx_info("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        conn_uta.get_tx_info("NM_199425.2", "NC_000020.10")   
    
def test_tx_info_ne_param():
    """Existing seqs."""  
    with pytest.raises(TypeError):
        conn_utarest.get_tx_info("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        conn_uta.get_tx_info("NM_199425.2", "fake")    
        
def test_tx_mapping_options_e():
    """Existing transcript."""
    u = conn_uta.get_tx_mapping_options("NM_000051.3")
    r = just_values(conn_utarest.get_tx_mapping_options("NM_000051.3").json())
    assert u == r
       
def test_tx_mapping_options_ne():
    """Nonexisting transcript."""
    u = conn_uta.get_tx_mapping_options("fake")
    r = just_values(conn_utarest.get_tx_mapping_options("fake").json())
    assert u == r
    
def test_similar_transcripts_e():
    """Existing transcript."""
    u = conn_uta.get_similar_transcripts("NM_000051.3")
    r = just_values(conn_utarest.get_similar_transcripts("NM_000051.3").json())
    assert u == r
    
def test_similar_transcripts_ne():
    """Nonexisting transcript."""
    u = conn_uta.get_similar_transcripts("fake")
    r = just_values(conn_utarest.get_similar_transcripts("fake").json())
    assert u == r
    
def test_pro_ac_for_tx_ac_e():
    """Existing transcript."""
    u = conn_uta.get_pro_ac_for_tx_ac("NM_000051.3")
    r = conn_utarest.get_pro_ac_for_tx_ac("NM_000051.3").json()
    assert u == r
    
def test_pro_ac_for_tx_ac_ne():
    """Nonexisting transcript."""   
    u = conn_uta.get_pro_ac_for_tx_ac("fake")
    r = conn_utarest.get_pro_ac_for_tx_ac("fake").json()
    assert u == r
    
def test_assembly_map_e():
    """Existing assembly name."""
    u = dict(conn_uta.get_assembly_map("GRCh38.p5"))
    r = conn_utarest.get_assembly_map("GRCh38.p5").json()
    assert u == r
    
def test_assembly_map_ne():
    """Nonexisting assembly name."""
    r = conn_utarest.get_assembly_map("GROUCH")
    assert r.status_code == 404
    with pytest.raises(Exception):
        conn_uta.get_assembly_map("GROUCH")
     
def test_data_version():
    u = conn_uta.data_version()
    r = conn_utarest.data_version()
    assert u == r
    
def test_schema_version():
    u = conn_uta.data_version()
    r = conn_utarest.data_version()
    assert u == r
    
def test_sequence_source():
    u = conn_uta.data_version()
    r = conn_utarest.data_version()
    assert u == r