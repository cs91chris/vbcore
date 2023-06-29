from unittest.mock import MagicMock, patch

from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.crypto.CryptoFactory")
def test_hash_encode(mock_crypto_factory, runner):
    mock_instance = MagicMock()
    mock_crypto_factory.instance.return_value = mock_instance

    result = runner.invoke(main, ["crypto", "hash-encode", "-t", "BCRYPT", "test"])

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_crypto_factory.instance.assert_called_once_with("BCRYPT")
    mock_instance.hash.assert_called_once_with("test")


@patch("vbcore.tools.crypto.CryptoFactory")
def test_hash_verify(mock_crypto_factory, runner):
    mock_instance = MagicMock()
    mock_crypto_factory.instance.return_value = mock_instance

    result = runner.invoke(
        main, ["crypto", "hash-verify", "-t", "BCRYPT", "hash-test", "test"]
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_crypto_factory.instance.assert_called_once_with("BCRYPT")
    mock_instance.verify.assert_called_once_with("hash-test", "test", raise_exc=True)
