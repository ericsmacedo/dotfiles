import unittest
from pathlib import Path
from unittest.mock import patch

from dotfiles.commands import run


class CommandTests(unittest.TestCase):
    def test_passes_arguments_without_a_shell(self):
        with patch("dotfiles.commands.subprocess.run") as subprocess_run:
            run("git", "-C", Path("directory with spaces"), "status", check=False)

        subprocess_run.assert_called_once_with(
            ["git", "-C", "directory with spaces", "status"],
            check=False,
            env=None,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
