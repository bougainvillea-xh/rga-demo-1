import pytest

import main


def test_main_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    main.main()
    assert capsys.readouterr().out == "Hello from rga-demo-1!\n"
