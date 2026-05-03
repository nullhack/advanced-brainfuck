import json
import os
import tempfile

from brainfuck import BrainFuck


class TestSaveLoadTape:
    """Tests for save_tape and load_tape methods."""

    def test_save_creates_json_with_pointer_and_cells(self):
        bf = BrainFuck()
        bf.execute("+++++>+++>++")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            bf.save_tape(path)
            with open(path) as f:
                data = json.load(f)
            assert data["pointer"] == 2
            assert data["cells"]["0"] == 5
            assert data["cells"]["1"] == 3
            assert data["cells"]["2"] == 2
        finally:
            os.unlink(path)

    def test_save_only_nonzero_cells(self):
        bf = BrainFuck()
        bf.execute("+++")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            bf.save_tape(path)
            with open(path) as f:
                data = json.load(f)
            assert "0" in data["cells"]
            assert data["cells"]["0"] == 3
            assert len(data["cells"]) == 1
        finally:
            os.unlink(path)

    def test_load_restores_pointer_and_cells(self):
        bf = BrainFuck()
        bf.execute("+++++>+++>++")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            bf.save_tape(path)
            bf2 = BrainFuck()
            bf2.load_tape(path)
            assert bf2.pointer == 2
            assert bf2.cells[0] == 5
            assert bf2.cells[1] == 3
            assert bf2.cells[2] == 2
        finally:
            os.unlink(path)

    def test_roundtrip_preserves_state(self, capsys):
        bf = BrainFuck()
        bf.execute("+++++++++++++++++++++++++++++++++++++++++++++++++++.")
        capsys.readouterr()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            bf.save_tape(path)
            bf2 = BrainFuck()
            bf2.load_tape(path)
            bf2.execute(".")
            captured = capsys.readouterr()
            assert captured.out == "3"
        finally:
            os.unlink(path)

    def test_save_default_path(self):
        bf = BrainFuck()
        bf.execute("+++")
        try:
            bf.save_tape()
            assert os.path.exists("tape.json")
            with open("tape.json") as f:
                data = json.load(f)
            assert data["cells"]["0"] == 3
        finally:
            if os.path.exists("tape.json"):
                os.unlink("tape.json")

    def test_load_empty_cells(self):
        data = {"pointer": 5, "cells": {}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(data, f)
            path = f.name
        try:
            bf = BrainFuck()
            bf.load_tape(path)
            assert bf.pointer == 5
            assert bf.cells[0] == 0
        finally:
            os.unlink(path)

    def test_load_negative_indices(self):
        data = {"pointer": -3, "cells": {"-3": 42, "-1": 10}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(data, f)
            path = f.name
        try:
            bf = BrainFuck()
            bf.load_tape(path)
            assert bf.pointer == -3
            assert bf.cells[-3] == 42
            assert bf.cells[-1] == 10
        finally:
            os.unlink(path)


class TestOutputFile:
    """Tests for output_file parameter in execute()."""

    def test_output_to_file(self):
        bf = BrainFuck()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            path = f.name
        try:
            with open(path, "w") as fh:
                bf.execute(
                    "+++++++++[>++++++++<-]>+.",
                    output_file=fh,
                )
            with open(path) as fh:
                assert fh.read() == "I"
        finally:
            os.unlink(path)

    def test_output_to_file_multiline(self):
        bf = BrainFuck()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name
        try:
            with open(path, "w") as fh:
                bf.execute(
                    "++++++++++.++++++++++.",
                    output_file=fh,
                )
            with open(path) as fh:
                content = fh.read()
                assert "\n" in content
        finally:
            os.unlink(path)

    def test_output_default_stdout(self, capsys):
        bf = BrainFuck()
        bf.execute("+++++++++[>++++++++<-]>+.")
        captured = capsys.readouterr()
        assert captured.out == "I"

    def test_output_none_same_as_stdout(self, capsys):
        bf = BrainFuck()
        bf.execute(
            "+++++++++[>++++++++<-]>+.",
            output_file=None,
        )
        captured = capsys.readouterr()
        assert captured.out == "I"


class TestCellWrapping:
    """Tests for 8-bit unsigned cell wrapping."""

    def test_overflow_wraps_to_zero(self):
        bf = BrainFuck()
        bf.execute("-")  # 255
        bf.execute("+")  # wraps to 0
        assert bf.cells[0] == 0

    def test_256_wraps_to_zero(self):
        bf = BrainFuck()
        bf.execute("+" * 256)
        assert bf.cells[0] == 0

    def test_underflow_wraps_to_255(self):
        bf = BrainFuck()
        bf.execute("-")
        assert bf.cells[0] == 255

    def test_double_underflow(self):
        bf = BrainFuck()
        bf.execute("--")
        assert bf.cells[0] == 254

    def test_wrapping_in_loop(self):
        bf = BrainFuck()
        bf.execute("+[-]")
        assert bf.cells[0] == 0

    def test_set_255_and_increment(self):
        bf = BrainFuck()
        bf.execute("-")
        assert bf.cells[0] == 255
        bf.execute("+")
        assert bf.cells[0] == 0
