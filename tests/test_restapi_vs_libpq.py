import requests
import pytest
import hgvs.dataproviders.uta as uta
import datetime
from typing import List

# The server you are using to test:
base = "http://127.0.0.1:8000"

conn = uta.connect()

# There are small descrepanices between http responses and uta return values
# although the two do not actually vary in content.
#
#             HTTP          |           UTA
#              ""           |           ''
#     str(datetime_object)  |      datetime_object
#           str(list)       |           list
#             null          |           None
# etc.
#
# There are strings nested in lists that are also strings, making for some
# complications. Several methods have been created to smooth out the small
# descrepanices:
#
# str_date, to_list, to_nested_list, to_dict, to_literal
#

def equals(a, b):
    """Equals method used to compare http response to uta output."""
    return(
        a == 'null' and b == None 
        or to_literal(a) == b
        or to_list(a) == b
        or to_nested_list(a) == b
        or to_list_str(a) == str_date(b)
        or equal_regardless_of_order(to_nested_list(a), b)   
    )
    
def str_date(l : list):
    """
    Formats date, if the last item in a list is the date.
    Example: datetime.datetime(2014, 2, 10, 22, 59, 21, 153414) to 2014-02-10T22:59:21.153414.
    """
    last = l[len(l)-1]
    if(type(last) == datetime.datetime):
        l[len(l)-1] = str(last).replace(" ", "T")
    return l

def to_list_str(ls : str):
    if ls == '[]': return []
    return ls.strip('][').strip('""').split('","') #if all are strings
    
def to_list(ls : str):
    if ls == '[]': return []
    newList = ls.strip('][').replace('"', '').split(',')
    for i in range(len(newList)):
        try: newList[i] = int(newList[i])
        except(Exception): continue
    return newList

def to_nested_list(ls : str) -> List[List]:
    if ls == '[]': return []
    newlist = []
    lists = ls.strip('][').strip('][').split('],[')
    for outer_list in lists:
        inner = outer_list.replace('"', '').split(',')
        for i in range(len(inner)):
            if inner[i] == 'null': inner[i] = None
            if inner[i] == 'true': inner[i] = True
            if inner[i] == 'false': inner[i] = False
            try: inner[i] = int(inner[i])
            except(Exception): continue
        newlist.append(inner)
    return newlist

def to_dict(d : str) -> dict:
    newdict = {}
    d = d.strip('}{').strip('"').split('","')
    for item in d:
        keyval = item.split('":"')
        newdict[keyval[0]] = keyval[1]
    return newdict

def to_literal(my_string : str):
    return my_string.strip('"')

# In addition, the uta method get_tx_for_gene does not always return 
# transcript info in the same order each time. Because the transcript info 
# is neither hashable or sortable, the following has been created to help 
# accurately compare the content of two lists.

def equal_regardless_of_order(list, other):
    for item in list:
        try:
            other.remove(item)
        except ValueError:
            return False
    return True
    
# TESTS #####################################################################################
    
@pytest.mark.skip(reason="slow")
def test_seq_e():
    """Exisiting seq."""
    url = base + "/seq/NC_000007.13"
    assert equals(requests.get(url).text), conn.get_seq("NC_000007.13")

def test_seq_ne():
    """Nonexisitng seq."""
    url = base + "/seq/fake"
    assert requests.get(url).status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn.get_seq("fake")
    
@pytest.mark.skip(reason="not fast")
def test_seq_e_indices():
    """Exisiting seq with start and end indices."""
    url = base + "/seq/NC_000007.13?start_i=10000&end_i=10050"
    assert equals(requests.get(url).text), conn.get_seq("NC_000007", 10000, 10050)

def test_acs_for_protein_seq_e():
    """Exisiting seq."""
    url = base + "/acs_for_protein_seq/MRAKWRKKRMRRLKRKRRKMRQRSK"
    assert equals(requests.get(url).text, conn.get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK"))

def test_acs_for_protein_seq_ne():
    """Nonexisiting seq."""
    url = base + "/acs_for_protein_seq/fake"
    assert equals(requests.get(url).text, conn.get_acs_for_protein_seq("fake"))

def test_acs_for_protein_seq_ne_nonalphabetical():
    """Non-alphabetic character seq."""
    url = base + "/acs_for_protein_seq/123"
    assert requests.get(url).status_code == 404
    with pytest.raises(RuntimeError):
        conn.get_acs_for_protein_seq("123")

def test_gene_info_e():
    """Existing gene."""
    url = base + "/gene_info/VHL"
    assert equals(requests.get(url).text, conn.get_gene_info("VHL"))
    
def test_gene_info_ne():
    """Nonexisitng gene."""
    url = base + "/gene_info/VH"
    assert equals(requests.get(url).text, conn.get_gene_info("VH"))
        
def test_tx_exons_e():
    """Exisiting seqs."""
    url = base + "/tx_exons/NM_199425.2/NC_000020.10?alt_aln_method=splign"
    assert equals(requests.get(url).text, conn.get_tx_exons("NM_199425.2", "NC_000020.10", "splign"))
    
def test_tx_exons_ne():
    """Nonexisting seq."""
    url = base + "/tx_exons/NM_199425.2/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn.get_tx_exons("NM_199425.2", "fake", "splign")
        
def test_tx_exons_e_params():
    """Existing seqs with missing param"""
    url = base + "/tx_exons/NM_199425.2/NC_000020.10"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_exons("NM_199425.2", "NC_000020.10")
        
def test_tx_exons_ne_params():
    """Nonexisting seq with missing param"""
    url = base + "/tx_exons/NM_199425.2/fake"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_exons("NM_199425.2", "fake")

def test_tx_for_gene_e():
    """Existing gene."""
    url = base + "/tx_for_gene/VHL"
    assert equals(requests.get(url).text, conn.get_tx_for_gene("VHL"))

def test_tx_for_gene_ne():
    """Nonexisitng gene."""
    url = base + "/tx_for_gene/VH"
    assert equals(requests.get(url).text, conn.get_tx_for_gene("VHL"))

# I can't find a set of parameters that returns something other than an empty list.
def test_tx_for_region_e():
    """Existing region."""
    url = base + "/tx_for_region/NC_000007.13?alt_aln_method=splign&start_i=10000&end_i=10050"
    assert equals(requests.get(url).text, conn.get_tx_for_region("NC_000007.13", "splign", 10000, 10050))
    
def test_tx_for_region_ne():
    """Nonexisting region"""
    url = base + "/tx_for_region/fake?alt_aln_method=splign&start_i=10000&end_i=10050"
    assert equals(requests.get(url).text, conn.get_tx_for_region("fake", "splign", 10000, 10050))
    
def test_tx_region_e_params():
    """Exisiting region with only some params."""
    url = base + "/tx_for_region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_for_region("NNC_000007.13", "splign")
    
def test_tx_region_ne_params():
    """Nonexisting region with only some params."""
    url = base + "/tx_for_region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_for_region("fake", "splign")

def test_alignments_for_region_e():
    """Existing region."""
    url = base + "/alignments_for_region/NC_000007.13?alt_aln_method=splign&start_i=10000&end_i=10050"
    assert equals(requests.get(url).text, conn.get_alignments_for_region("NC_000007.13", 10000, 10050, "splign"))
    
def test_alignments_for_region_ne():
    """Nonexisting region"""
    url = base + "/alignments_for_region/fake?alt_aln_method=splign&start_i=10000&end_i=10050"
    assert equals(requests.get(url).text, conn.get_alignments_for_region("fake", 10000, 10050, "splign"))
    
def test_alignments_region_e_params():
    """Exisiting region with only some params."""
    url = base + "/alignments_for_region/NC_000007.13?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_alignments_for_region("NNC_000007.13", "splign")
    
def test_alignments_region_ne_params():
    """Nonexisting region with only some params."""
    url = base + "/alignments_for_region/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_alignments_for_region("fake", "splign")
        
#def test_tx_identity_info_e()

#def test_tx_identity_info_ne()

def test_tx_info_e():
    """Existing seqs."""
    url = base + "/tx_info/NM_199425.2/NC_000020.10?alt_aln_method=splign"
    assert equals(requests.get(url).text, conn.get_tx_info("NM_199425.2", "NC_000020.10", "splign"))
    
def test_tx_info_ne():
    """Nonexisting seq."""
    url = base + "/tx_info/NM_199425.2/fake?alt_aln_method=splign"
    assert requests.get(url).status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        conn.get_tx_info("NM_199425.2", "fake", "splign")
        
def test_tx_info_e_params():
    """Nonexisting region with only some params."""
    url = base + "/tx_info/NM_199425.2/NC_000020.10"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_info("NM_199425.2", "NC_000020.10")
        
def test_tx_info_ne_params():
    """Nonexsiting seq."""
    url = base + "/tx_info/NM_199425.2/fake"
    assert requests.get(url).status_code == 422
    with pytest.raises(TypeError):
        conn.get_tx_info("NM_199425.2", "fake")
        
def test_tx_mapping_options_e():
    """Existing transcript."""
    url = base + "/tx_mapping_options/NM_000051.3"
    assert equals(requests.get(url).text, conn.get_tx_mapping_options("NM_000051.3"))
    
def test_tx_mapping_options_ne():
    """Nonexisting transcript."""
    url = base + "/tx_mapping_options/fake"
    assert equals(requests.get(url).text, conn.get_tx_mapping_options("fake"))

def test_similar_transcripts_e():
    """Existing transcript."""
    url = base + "/similar_transcripts/NM_000051.3"
    assert equals(requests.get(url).text, conn.get_similar_transcripts("NM_000051.3"))

def test_similar_transcripts_ne():
    """Nonexisting transcript."""
    url = base + "/similar_transcripts/fake"
    assert equals(requests.get(url).text, conn.get_similar_transcripts("fake"))
    
def test_pro_ac_for_tx_ac_e():
    """Existing transcript."""
    url = base + "/pro_ac_for_tx_ac/NM_000051.3"
    assert equals(requests.get(url).text, conn.get_pro_ac_for_tx_ac("NM_000051.3"))
    
def test_pro_ac_for_tx_ac_ne():
    """Nonexisting transcript."""
    url = base + "/pro_ac_for_tx_ac/fake"
    assert equals(requests.get(url).text, conn.get_pro_ac_for_tx_ac("fake"))
    
def test_assembly_map_e():
    """Existing assembly name."""
    url = base + "/assembly_map/GRCh38.p5"
    assert to_dict(requests.get(url).text) == conn.get_assembly_map("GRCh38.p5")

def test_assembly_map_ne():
    """Nonexisting assembly name."""
    url = base + "/assembly_map/GROUCH"
    assert requests.get(url).status_code == 404
    with pytest.raises(Exception):
        conn.get_assembly_map("GROUCH")
        