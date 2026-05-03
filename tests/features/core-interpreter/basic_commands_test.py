from brainfuck import BrainFuck


def test_execute_core_execute(capsys) -> None:
    """
    Given a new BrainFuck instance
    When I execute '++++++++++++++++++++++++++++++++++++++++++++++++++.'
    Then the output is '2'
    """
    bf = BrainFuck()
    bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++.')
    captured = capsys.readouterr()
    assert captured.out == '2'


def test_balance_core_balance_true() -> None:
    """
    Given a new BrainFuck instance
    When I check if '[[-][-][][{sum}+++.>]]' is balanced
    Then the result is True
    """
    assert BrainFuck.is_balanced('[[-][-][][{sum}+++.>]]') is True


def test_balance_core_balance_false_missing_close() -> None:
    """
    Given a new BrainFuck instance
    When I check if '[.[>>>[+++{sum]<<+++.]*]' is balanced
    Then the result is False
    """
    assert BrainFuck.is_balanced('[.[>>>[+++{sum]<<+++.]*]') is False


def test_balance_core_balance_false_extra_close() -> None:
    """
    Given a new BrainFuck instance
    When I check if '[.[>>>[+++[{sum}<<+++.]*]' is balanced
    Then the result is False
    """
    assert BrainFuck.is_balanced('[.[>>>[+++[{sum}<<+++.]*]') is False


def test_display_core_print_cells(capsys) -> None:
    """
    Given a new BrainFuck instance with cell 0 set to 50
    When I execute '*'
    Then the output shows '|50|'
    """
    bf = BrainFuck()
    bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++*')
    captured = capsys.readouterr()
    assert '|50|' in captured.out


def test_display_core_print_history(capsys) -> None:
    """
    Given a new BrainFuck instance that has executed commands
    When I execute '&'
    Then the output shows the length and content of all executed commands
    """
    bf = BrainFuck()
    bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++.')
    bf.execute('[-]')
    bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++.*------------------------------------------------*&')
    captured = capsys.readouterr()
    lines = captured.out.strip().split('\n')
    history_line = lines[-1]
    assert '++++++++++++++++++++++++++++++++++++++++++++++++++' in history_line


def test_repl_core_repl(monkeypatch) -> None:
    """
    Given a new BrainFuck instance
    When I call interpreter()
    Then an interactive REPL starts with ">>" prompt
    And typing "help" shows command reference
    And an empty line exits the REPL
    """
    bf = BrainFuck()
    inputs = iter(['help', ''])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    bf.interpreter()
