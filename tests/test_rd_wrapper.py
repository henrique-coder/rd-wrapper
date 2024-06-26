from pytest import raises
from rd_wrapper import RDW, Exceptions


def test_rd_wrapper():
    with raises(Exceptions.MissingCredentials):
        RDW()
