from rise.main import main


def test_main_imports_and_is_callable() -> None:
    """The main module should import cleanly and expose the entry point."""
    assert callable(main)
