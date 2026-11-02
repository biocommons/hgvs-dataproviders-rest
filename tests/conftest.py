import pytest


@pytest.fixture(scope="module")
def vcr_cassette_dir(pytestconfig):
    return str(pytestconfig.rootpath / "tests" / "cassettes")
