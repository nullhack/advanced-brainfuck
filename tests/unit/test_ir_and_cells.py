"""Unit contract tests for IR compilation and numeric conversion internals.

These tests verify implementation contracts not covered by BDD feature tests.
They belong in tests/unit/ because they exercise internal methods (_compile_to_ir,
convert_ir_to_numeric) rather than the public API entry points.
"""
from brainfuck import (
    OP_ADD,
    OP_JUMP_NZ,
    OP_JUMP_ZERO,
    OP_MOVE,
    OP_OUTPUT,
    BrainFuck,
    Cells,
    convert_ir_to_numeric,
)


class TestIRCompilation:
    """Contract tests for _compile_to_ir."""

    def test_add_rle_collapses_five_increments(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('+++++')
        assert ir == [('add', 5)]

    def test_sub_rle_collapses_five_decrements(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('-----')
        assert ir == [('add', -5)]

    def test_move_right_rle(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('>>>')
        assert ir == [('move', 3)]

    def test_move_left_rle(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('<<<')
        assert ir == [('move', -3)]

    def test_mixed_commands_not_collapsed(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('+.')
        assert ir == [('add', 1), ('output',)]

    def test_jump_targets_patched(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('[-]')
        assert ir[0] == ('jump_zero', 3)
        assert ir[1] == ('add', -1)
        assert ir[2] == ('jump_nz', 0)

    def test_nested_loops_patched(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('[->[+]]')
        jump_zeros = [op for op in ir if op[0] == 'jump_zero']
        jump_nzs = [op for op in ir if op[0] == 'jump_nz']
        assert len(jump_zeros) == 2
        assert len(jump_nzs) == 2

    def test_empty_program_returns_empty_ir(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('')
        assert ir == []

    def test_non_bf_chars_filtered(self):
        bf = BrainFuck()
        ir = bf._compile_to_ir('hello world+++')
        assert ir == [('add', 3)]


class TestNumericIRConversion:
    """Contract tests for convert_ir_to_numeric."""

    def test_add_opcode(self):
        result = convert_ir_to_numeric([('add', 5)])
        assert result[0, 0] == OP_ADD
        assert result[0, 1] == 5

    def test_move_opcode(self):
        result = convert_ir_to_numeric([('move', -3)])
        assert result[0, 0] == OP_MOVE
        assert result[0, 1] == -3

    def test_output_opcode(self):
        result = convert_ir_to_numeric([('output',)])
        assert result[0, 0] == OP_OUTPUT
        assert result[0, 1] == 0

    def test_jump_opcodes(self):
        result = convert_ir_to_numeric([('jump_zero', 5), ('add', 1), ('jump_nz', 0)])
        assert result[0, 0] == OP_JUMP_ZERO
        assert result[0, 1] == 5
        assert result[2, 0] == OP_JUMP_NZ
        assert result[2, 1] == 0

    def test_empty_ir_returns_empty_array(self):
        result = convert_ir_to_numeric([])
        assert len(result) == 0


class TestCells:
    """Contract tests for Cells internal behaviour."""

    def test_default_value_is_zero(self):
        cells = Cells()
        assert cells[0] == 0

    def test_set_and_get(self):
        cells = Cells()
        cells[5] = 42
        assert cells[5] == 42

    def test_zero_value_deletes_key(self):
        cells = Cells()
        cells[5] = 42
        cells[5] = 0
        assert cells[5] == 0

    def test_negative_index_via_sparse(self):
        cells = Cells()
        cells[-1] = 99
        assert cells[-1] == 99

    def test_backup_is_independent(self):
        cells = Cells()
        cells[0] = 10
        backup = cells.backup()
        cells[0] = 999
        assert backup[0] == 10

    def test_print_pos_shows_pointer(self):
        cells = Cells()
        cells[0] = 5
        result = cells.print_pos(0)
        assert '|5|' in result
