# Workflow commands use Bash environment assignments on every platform.
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    git = shutil.which("git")
    git_bash = Path(git).parent.parent / "bin" / "bash.exe" if git else None
    shell.executable(str(git_bash) if git_bash and git_bash.is_file() else "bash")

include: "workflow/Snakefile"
