from unittest.mock import Mock

from hgvs_dataproviders_rest.restclient import UTAREST


def test_optional_parameters_keep_zero_values():
    assert UTAREST.optional_parameters(None, ["start_i", "end_i"], [0, 50]) == "?start_i=0&end_i=50"


def test_get_alignments_for_region_passes_alignment_method(monkeypatch):
    client = UTAREST.__new__(UTAREST)
    client.server = "http://example.test"
    response = Mock()
    response.json.return_value = []
    get = Mock(return_value=response)
    monkeypatch.setattr("hgvs_dataproviders_rest.restclient.requests.get", get)

    assert client.get_alignments_for_region("NC_000007.13", 0, 50, "splign") == []

    get.assert_called_once_with(
        "http://example.test/alignments_for_region/NC_000007.13?start_i=0&end_i=50&alt_aln_method=splign",
        timeout=5,
    )


def test_get_similar_transcripts_allows_slow_response(monkeypatch):
    client = UTAREST.__new__(UTAREST)
    client.server = "http://example.test"
    response = Mock()
    response.json.return_value = []
    get = Mock(return_value=response)
    monkeypatch.setattr("hgvs_dataproviders_rest.restclient.requests.get", get)

    assert client.get_similar_transcripts("NM_000051.3") == []

    get.assert_called_once_with("http://example.test/similar_transcripts/NM_000051.3", timeout=120)
