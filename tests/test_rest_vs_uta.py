import datetime
import os

import hgvs.dataproviders.uta as uta
import pytest
import yaml
from vcr.filters import decode_response

import hgvs_dataproviders_rest.restclient as utarest

os.environ["HGVS_DATAPROVIDER_REST_URL"] = "http://127.0.0.1:8000"  # Used in restclient.connect()


def equal_regardless_of_order(list, other):
    """To compare lists that are neither hashable or stortable."""
    for item in list:
        try:
            other.remove(item)
        except ValueError:
            return False
    return True


def yaml_decode(test_name: str) -> str:
    """Opens a yaml file, gets the response, and returns it decoded."""
    file_path = ("tests/cassettes/{test}.yaml").format(test=test_name)
    with open(file_path, "r") as f:
        yam = yaml.safe_load(f)
    response = yam["interactions"][0]["response"]
    yam_decode = decode_response(response)["body"]["string"]
    if isinstance(yam_decode, bytes):
        byte_decode = yam_decode.decode("utf-8")
        piece = byte_decode.split("\n")[1]
        return piece
    return yam_decode


#########################################################################
# u = UTA
# r = UTA Rest


@pytest.mark.skip(reason="super slow")
def test_seq_e():
    """Existing seq."""
    u = uta.connect().get_seq("NC_000007.13")
    r = utarest.connect().get_seq("NC_000007.13")
    assert u == r


@pytest.mark.vcr
def test_seq_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_seq("fake")
    assert "Failed to fetch" in r["detail"]
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_seq("fake")


@pytest.mark.vcr
def test_seq_e_indices():
    """Existing seq with start and end indices."""
    # u = uta.connect().get_seq("NC_000007.13", 10000, 10050)
    u = yaml_decode("test_seq_e_indices")
    r = utarest.connect().get_seq("NC_000007.13", 10000, 10050)
    assert u == r


@pytest.mark.vcr
def test_acs_for_protein_seq_e():
    """Existing seq."""
    u = uta.connect().get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK")
    r = utarest.connect().get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK")
    assert u == r


@pytest.mark.vcr
def test_acs_for_protein_seq_ne():
    """Nonexisting seq."""
    u = uta.connect().get_acs_for_protein_seq("fake")
    r = utarest.connect().get_acs_for_protein_seq("fake")
    assert u == r


@pytest.mark.vcr
def test_acs_for_protein_seq_ne_nonalphabetical():
    """Non-alphabetic character seq."""
    r = utarest.connect().get_acs_for_protein_seq("123")
    assert "Normalized sequence contains non-alphabetic characters" in r["detail"]
    with pytest.raises(RuntimeError):
        uta.connect().get_acs_for_protein_seq("123")


@pytest.mark.vcr
def test_gene_info_e():
    """Existing gene."""
    u = dict(uta.connect().get_gene_info("VHL"))
    r = utarest.connect().get_gene_info("VHL")
    r["added"] = datetime.datetime.fromisoformat(r["added"])
    assert u == r


@pytest.mark.vcr
def test_gene_info_ne():
    """Nonexisting gene."""
    u = uta.connect().get_gene_info("VH")
    r = utarest.connect().get_gene_info("VH")
    assert u == r


@pytest.mark.vcr
def test_tx_exons_e():
    """Existing seqs."""
    u = uta.connect().get_tx_exons("NM_199425.2", "NC_000020.10", "splign")
    r = [list(t.values()) for t in utarest.connect().get_tx_exons("NM_199425.2", "NC_000020.10", "splign")]
    assert u == r


@pytest.mark.vcr
def test_tx_exons_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_tx_exons("NM_199425.2", "fake", "splign")
    assert "No tx_exons for" in r["detail"]
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_exons("NM_199425.2", "fake", "splign")


@pytest.mark.vcr
def test_tx_exons_e_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_exons("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        uta.connect().get_tx_exons("NM_199425.2", "NC_000020.10")


@pytest.mark.vcr
def test_tx_exons_ne_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_exons("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        uta.connect().get_tx_exons("NM_199425.2", "fake")


@pytest.mark.vcr
def test_tx_for_gene_e():
    """Existing gene."""
    u = uta.connect().get_tx_for_gene("VHL")
    r0 = utarest.connect().get_tx_for_gene("VHL")
    r = [list(t.values()) for t in r0]
    assert equal_regardless_of_order(u, r)


@pytest.mark.vcr
def test_tx_for_gene_ne():
    """Nonexisitng gene."""
    u = uta.connect().get_tx_for_gene("VH")
    r = utarest.connect().get_tx_for_gene("VH")
    assert u == r


@pytest.mark.vcr
def test_tx_for_region_e():  # Need example
    """Existing region."""
    u = uta.connect().get_tx_for_region("NC_000007.13", "splign", 0, 50)
    r = [list(t.values()) for t in utarest.connect().get_tx_for_region("NC_000007.13", "splign", 0, 50)]
    assert u == r


@pytest.mark.vcr
def test_tx_for_region_ne():
    """Nonexisting region"""
    u = uta.connect().get_tx_for_region("fake", "splign", 0, 50)
    r = utarest.connect().get_tx_for_region("fake", "splign", 0, 50)
    assert u == r


@pytest.mark.vcr
def test_tx_for_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_for_region("NC_000007.13", "splign")
    with pytest.raises(TypeError):
        uta.connect().get_tx_for_region("NC_000007.13", "splign")


@pytest.mark.vcr
def test_tx_for_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_for_region("fake", "splign")
    with pytest.raises(TypeError):
        uta.connect().get_tx_for_region("fake", "splign")


@pytest.mark.vcr
def test_alignments_for_region_e():  # Need example
    """Existing region."""
    u = uta.connect().get_alignments_for_region("NC_000007.13", 0, 50)
    r = utarest.connect().get_alignments_for_region("NC_000007.13", 0, 50)
    assert u == r


@pytest.mark.vcr
def test_alignments_for_region_ne():
    """Nonexisting region"""
    u = uta.connect().get_alignments_for_region("fake", 0, 50)
    r = utarest.connect().get_alignments_for_region("fake", 0, 50)
    assert u == r


@pytest.mark.vcr
def test_alignments_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_alignments_for_region("NC_000007.13")
    with pytest.raises(TypeError):
        uta.connect().get_alignments_for_region("NC_000007.13")


@pytest.mark.vcr
def test_alignments_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_alignments_for_region("fake")
    with pytest.raises(TypeError):
        uta.connect().get_alignments_for_region("fake")


@pytest.mark.vcr
def test_tx_identity_info_e():
    """Existing transcript."""
    u = dict(uta.connect().get_tx_identity_info("NM_199425.2"))
    r = utarest.connect().get_tx_identity_info("NM_199425.2")
    assert u == r


@pytest.mark.vcr
def test_tx_identity_info_ne():
    """Nonexisting transcript."""
    r = utarest.connect().get_tx_identity_info("fake")
    assert "No transcript definition for" in r["detail"]
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_identity_info("fake")


@pytest.mark.vcr
def test_tx_info_e():
    """Existing seqs."""
    u = dict(uta.connect().get_tx_info("NM_199425.2", "NC_000020.10", "splign"))
    r = utarest.connect().get_tx_info("NM_199425.2", "NC_000020.10", "splign")
    assert u == r


@pytest.mark.vcr
def test_tx_info_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_tx_info("NM_199425.2", "fake", "splign")
    assert "No tx_info for" in r["detail"]
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_info("NM_199425.2", "fake", "splign")


@pytest.mark.vcr
def test_tx_info_e_param():
    """Existing seqs."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_info("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        uta.connect().get_tx_info("NM_199425.2", "NC_000020.10")


@pytest.mark.vcr
def test_tx_info_ne_param():
    """Existing seqs."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_info("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        uta.connect().get_tx_info("NM_199425.2", "fake")


@pytest.mark.vcr
def test_tx_mapping_options_e():
    """Existing transcript."""
    u = uta.connect().get_tx_mapping_options("NM_000051.3")
    r = [list(t.values()) for t in utarest.connect().get_tx_mapping_options("NM_000051.3")]
    assert u == r


@pytest.mark.vcr
def test_tx_mapping_options_ne():
    """Nonexisting transcript."""
    u = uta.connect().get_tx_mapping_options("fake")
    r = utarest.connect().get_tx_mapping_options("fake")
    assert u == r


@pytest.mark.vcr
def test_similar_transcripts_e():
    """Existing transcript."""
    u = uta.connect().get_similar_transcripts("NM_000051.3")
    r = [list(t.values()) for t in utarest.connect().get_similar_transcripts("NM_000051.3")]
    assert u == r


@pytest.mark.vcr
def test_similar_transcripts_ne():
    """Nonexisting transcript."""
    u = uta.connect().get_similar_transcripts("fake")
    r = utarest.connect().get_similar_transcripts("fake")
    assert u == r


@pytest.mark.vcr
def test_pro_ac_for_tx_ac_e():
    """Existing transcript."""
    u = uta.connect().get_pro_ac_for_tx_ac("NM_000051.3")
    r = utarest.connect().get_pro_ac_for_tx_ac("NM_000051.3")
    assert u == r


@pytest.mark.vcr
def test_pro_ac_for_tx_ac_ne():
    """Nonexisting transcript."""
    u = uta.connect().get_pro_ac_for_tx_ac("fake")
    r = utarest.connect().get_pro_ac_for_tx_ac("fake")
    assert u == r


@pytest.mark.vcr
def test_assembly_map_e():
    """Existing assembly name."""
    u = uta.connect().get_assembly_map("GRCh38.p5")
    r = utarest.connect().get_assembly_map("GRCh38.p5")
    assert u == r


@pytest.mark.vcr
def test_assembly_map_ne():
    """Nonexisting assembly name."""
    r = utarest.connect().get_assembly_map("GROUCH")
    assert "No such file or directory" in r["detail"]
    assert ".gz" in r["detail"]
    with pytest.raises(Exception):
        uta.connect().get_assembly_map("GROUCH")


@pytest.mark.vcr
def test_data_version():
    u = uta.connect().data_version()
    r = utarest.connect().data_version()
    assert u == r


@pytest.mark.vcr
def test_schema_version():
    u = uta.connect().schema_version()
    r = utarest.connect().schema_version()
    assert u == r
