"""Node.js installation through NVM."""

import os
import tempfile
from pathlib import Path

from .commands import run

NVM_VERSION = "v0.39.7"
NVM_INSTALL_URL = (
    f"https://raw.githubusercontent.com/nvm-sh/nvm/{NVM_VERSION}/install.sh"
)


def install_nodejs(home: Path = Path.home()) -> None:
    """Install NVM and the current Node.js LTS release."""

    environment = dict(os.environ)
    environment.update(
        {
            "HOME": str(home),
            "NVM_DIR": str(home / ".nvm"),
            "PROFILE": "/dev/null",
        }
    )

    with tempfile.TemporaryDirectory(prefix="dotfiles-nvm-") as directory:
        script = Path(directory) / "install.sh"
        run("curl", "-fsSL", NVM_INSTALL_URL, "-o", script)
        run("bash", script, env=environment)

    run(
        "bash",
        "-c",
        (
            'source "$NVM_DIR/nvm.sh"'
            " && nvm install --lts"
            ' && nvm alias default "lts/*"'
            " && nvm use --lts"
        ),
        env=environment,
    )
    print(f"✅ Node.js LTS installed through NVM {NVM_VERSION}.")
