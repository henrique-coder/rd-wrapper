from pytest import raises
from rd_wrapper import RDW, Exceptions


def test_missing_credentials_exception() -> None:
    """
    Test if the MissingCredentials exception is raised when trying to instantiate the RDW class without any credentials.
    """

    with raises(Exceptions.MissingCredentials):
        rdw = RDW()
