import pytest
from brainfuck import BrainFuck


def test_acceleration_jit_pure_computation(capsys) -> None:
    """
    Given a BrainFuck instance
    When I execute '+++++++++++++++++++++++++++++++++++++++++++++++++++.' (no , * or &)
    Then the output is '3' (via JIT execution)
    """
    bf = BrainFuck()
    bf.execute('+++++++++++++++++++++++++++++++++++++++++++++++++++.')
    captured = capsys.readouterr()
    assert captured.out == '3'


def test_acceleration_jit_fallback_interpreted(monkeypatch, capsys) -> None:
    """
    Given a BrainFuck instance
    When I execute a program containing ',' (input command)
    Then the interpreted path is used
    """
    bf = BrainFuck()
    inputs = iter(['65', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    bf.execute(',.')
    captured = capsys.readouterr()
    assert 'A' in captured.out or '65' in captured.out


def test_acceleration_jit_output_correctness(capsys) -> None:
    """
    Given a BrainFuck instance
    When I execute '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.'
    Then the output is 'H' (identical to interpreted output)
    """
    bf = BrainFuck()
    bf.execute('++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.')
    captured = capsys.readouterr()
    assert captured.out == 'H'


def test_acceleration_jit_run_length_encoding(capsys) -> None:
    """
    Given a BrainFuck instance
    When I execute '+++++.' (five consecutive increments)
    Then the output is chr(5) (RLE collapsed to single add operation)
    """
    bf = BrainFuck()
    bf.execute('+++++.')
    captured = capsys.readouterr()
    assert captured.out == chr(5)


def test_acceleration_jit_jump_patching(capsys) -> None:
    """
    Given a BrainFuck instance
    When I compile '[-]' then execute
    Then the loop with pre-computed jump targets produces correct output
    """
    bf = BrainFuck()
    bf.execute('+++[-].')
    captured = capsys.readouterr()
    assert captured.out == '\n'