from pytest import raises
from rd_wrapper import RDW, APIToken, Exceptions


def test_rdw_missing_credentials_exception() -> None:
    """
    Test if the MissingCredentials exception is raised when trying to instantiate the RDW class without any credentials.
    """

    with raises(Exceptions.MissingCredentials):
        RDW()

def test_rdw_anonymous_access_parameter() -> None:
    """
    Test if the RDW class can be instantiated with anonymous access
    """

    rdw = RDW(anonymous_access=True)
    assert isinstance(rdw, RDW)

def test_rdw_get_server_time_method() -> None:
    """
    Test if the get_server_time method returns a string or an integer
    """

    rdw = RDW(anonymous_access=True)
    server_time = rdw.get_server_time()
    assert isinstance(server_time, (str, int))

def test_rdw_get_server_iso_time_method() -> None:
    """
    Test if the get_server_iso_time method returns a string or an integer
    """

    rdw = RDW(anonymous_access=True)
    server_iso_time = rdw.get_server_iso_time()
    assert isinstance(server_iso_time, (str, int))
