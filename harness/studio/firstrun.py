"""What has to be true before the studio can start a server, and how to make it so.

**A fresh clone has no `server.json`, and the dataclass default checkpoint is a
nano run only the training machine has.** Left alone, the studio would spawn a
server that dies on a missing file and show a fifteen-line crash tail to
somebody who has done nothing wrong yet. This module is the check the page
runs before that happens, and the one write that fixes it: pick a checkpoint
that is actually on disk, switch packs on, create the folder, save the file.

No web framework here, so `scripts/check_studio.py` can drive the whole of it
against a temporary repo layout. The page renders what `reasons` returns and calls
`bootstrap` with what the person picked; it decides nothing itself.

The download is deliberately not done from here. The weights are a gigabyte
from wherever the release is hosted, and fetching a file that size into a
folder is a thing a person should start on purpose -- so `WEIGHTS_HINT` says
where they go and `checkpoints` finds them once they are there.
"""

from __future__ import annotations

from pathlib import Path

from ..serverconfig import ServerConfig

# The checkpoint the release triple was read on (docs/RELEASE.md). Listed
# first when it is present; a machine with several checkpoints still gets a
# choice.
SHIPPED = "corn_jr_260m_v4_ft_social8"

# Where a downloaded release lands, relative to the repo root. The studio's
# checkpoint picker globs exactly this shape.
CKPT_DIR = "checkpoints"
CKPT_FILE = "ckpt.pt"

WEIGHTS_HINT = (
    f"Put the released weights at {CKPT_DIR}/<name>/{CKPT_FILE} inside this "
    f"folder -- the release page and README say where to download them -- "
    f"then press Rescan.")

DEFAULT_PACKS = "packs"


def checkpoints(repo: Path) -> list[str]:
    """Every `checkpoints/*/ckpt.pt` under the repo, as forward-slash paths
    relative to it, the shipped one first when it is there."""
    root = Path(repo) / CKPT_DIR
    found = sorted(
        str(p.relative_to(repo)).replace("\\", "/")
        for p in root.glob(f"*/{CKPT_FILE}")) if root.is_dir() else []
    shipped = f"{CKPT_DIR}/{SHIPPED}/{CKPT_FILE}"
    if shipped in found:
        found.remove(shipped)
        found.insert(0, shipped)
    return found


def missing_checkpoint(cfg: ServerConfig, repo: Path) -> str | None:
    """The configured checkpoint path when the file is not on disk, else None.

    An absolute path is honoured as written; a relative one is against the
    repo root, which is the cwd the supervisor starts the server in."""
    p = Path(cfg.ckpt)
    if not p.is_absolute():
        p = Path(repo) / p
    return None if p.is_file() else cfg.ckpt


def reasons(cfg: ServerConfig, cfg_path: Path, repo: Path) -> list[str]:
    """Why the page should show its setup card, in the order a person reads
    them. Empty means the instance is configured enough to start."""
    out = []
    if not Path(cfg_path).exists():
        out.append(f"no {Path(cfg_path).name} yet -- this is a first run")
    missing = missing_checkpoint(cfg, repo)
    if missing:
        out.append(f"the configured checkpoint is not on disk: {missing}")
    if not cfg.packs:
        out.append("no packs folder is configured, so he has none of your "
                   "data to answer from")
    return out


def blocking(cfg: ServerConfig, repo: Path) -> str | None:
    """The one reason the server must not be started at all -- a checkpoint
    that is not there. Everything else in `reasons` is advice."""
    missing = missing_checkpoint(cfg, repo)
    if missing:
        return (f"not starting the server: checkpoint {missing} is not on "
                f"disk. {WEIGHTS_HINT}")
    return None


def bootstrap(cfg: ServerConfig, cfg_path: Path, repo: Path, ckpt: str,
              packs: str = DEFAULT_PACKS) -> None:
    """Point the instance at a checkpoint and a packs folder and write the
    file. Mutates `cfg` in place so the open page keeps describing the file
    it just wrote."""
    cfg.ckpt = ckpt
    cfg.packs = packs
    if packs:
        (Path(repo) / packs).mkdir(exist_ok=True)
    cfg.validate()
    cfg.save(Path(cfg_path))
