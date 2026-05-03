import json
import os
import subprocess
import sys
import tempfile


def run_cli(*args, input_text=None):
    cmd = [sys.executable, "-m", "brainfuck"] + list(args)
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


class TestCLIOutputFlag:
    def test_output_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            outpath = f.name
        try:
            result = run_cli(
                "-c",
                "--output",
                outpath,
                "+++++++++[>++++++++<-]>+.",
            )
            assert result.returncode == 0
            with open(outpath) as f:
                assert f.read() == "I"
        finally:
            os.unlink(outpath)

    def test_output_file_not_stdout(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            outpath = f.name
        try:
            result = run_cli(
                "-c",
                "--output",
                outpath,
                "+++++++++++++++++++++++++++.",
            )
            assert result.returncode == 0
            assert result.stdout == ""
            with open(outpath) as f:
                assert f.read() != ""
        finally:
            os.unlink(outpath)


class TestCLIDumpFlag:
    def test_dump_creates_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            dumppath = f.name
        try:
            result = run_cli("-c", "--dump", dumppath, "+++")
            assert result.returncode == 0
            with open(dumppath) as f:
                data = json.load(f)
            assert data["cells"]["0"] == 3
        finally:
            os.unlink(dumppath)

    def test_dump_captures_final_state(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            dumppath = f.name
        try:
            result = run_cli("-c", "--dump", dumppath, "+++>++++")
            assert result.returncode == 0
            with open(dumppath) as f:
                data = json.load(f)
            assert data["pointer"] == 1
            assert data["cells"]["0"] == 3
            assert data["cells"]["1"] == 4
        finally:
            os.unlink(dumppath)


class TestCLILoadFlag:
    def test_load_restores_tape(self):
        tape_data = {"pointer": 0, "cells": {"0": 65}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(tape_data, f)
            loadpath = f.name
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            outpath = f.name
        try:
            result = run_cli(
                "-c",
                "--load",
                loadpath,
                "--output",
                outpath,
                ".",
            )
            assert result.returncode == 0
            with open(outpath) as f:
                assert f.read() == "A"
        finally:
            os.unlink(loadpath)
            os.unlink(outpath)

    def test_load_and_dump_roundtrip(self):
        tape_data = {"pointer": 0, "cells": {"0": 10}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(tape_data, f)
            loadpath = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            dumppath = f.name
        try:
            result = run_cli(
                "-c",
                "--load",
                loadpath,
                "--dump",
                dumppath,
                "+++",
            )
            assert result.returncode == 0
            with open(dumppath) as f:
                data = json.load(f)
            assert data["pointer"] == 0
            assert data["cells"]["0"] == 13
        finally:
            os.unlink(dumppath)
            os.unlink(loadpath)


class TestCLICombinedFlags:
    def test_load_output_dump_together(self):
        tape_data = {"pointer": 0, "cells": {"0": 72}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(tape_data, f)
            loadpath = f.name
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            outpath = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            dumppath = f.name
        try:
            result = run_cli(
                "-c",
                "--load",
                loadpath,
                "--output",
                outpath,
                "--dump",
                dumppath,
                ".",
            )
            assert result.returncode == 0
            with open(outpath) as f:
                assert f.read() == "H"
            with open(dumppath) as f:
                data = json.load(f)
            assert data["pointer"] == 0
            assert data["cells"]["0"] == 72
        finally:
            os.unlink(loadpath)
            os.unlink(outpath)
            os.unlink(dumppath)
