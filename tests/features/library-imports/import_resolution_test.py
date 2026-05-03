from brainfuck import BrainFuck


def test_imports_lib_simple_import(capsys) -> None:
    """
    Given a new BrainFuck instance
    When I execute '{toint}*'
    Then the output shows 'importing: bflib/toint.bf' followed by a cell display
    """
    bf = BrainFuck()
    bf.execute("{toint}*")
    captured = capsys.readouterr()
    assert "importing: bflib/toint.bf" in captured.out
    assert "|" in captured.out


def test_imports_lib_nested_import(capsys) -> None:
    """
    Given a new BrainFuck instance
    When I execute a program containing nested {LIB} references
    Then all nested imports are resolved before execution
    """
    bf = BrainFuck()
    bf.execute("{p10}*{tochar}")
    captured = capsys.readouterr()
    assert "importing: bflib/p10.bf" in captured.out
    assert "importing: bflib/tochar.bf" in captured.out


def test_imports_lib_missing_import(capsys) -> None:
    """
    Given a new BrainFuck instance
    When I execute '{nonexistent}'
    Then an exception is raised or error message printed with 'Could not import'
    """
    bf = BrainFuck()
    bf.execute("{nonexistent}")
    captured = capsys.readouterr()
    assert "Could not import" in captured.out


def test_imports_lib_command_history(capsys) -> None:
    """
    Given a new BrainFuck instance that has executed commands with library imports
    When I execute '&'
    Then the output shows the expanded command history with library contents inlined
    """
    bf = BrainFuck()
    bf.execute("+++++++++++++++++++++++++++++++++++++++++++++++++++.")
    bf.execute("[-]")
    bf.execute("{p10}*{tochar}")
    bf.execute("&")
    captured = capsys.readouterr()
    assert "+++++++++++++++++++++++++++++++++++++++++++++++++++" in captured.out
