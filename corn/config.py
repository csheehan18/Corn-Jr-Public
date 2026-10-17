"""Every knob in one place.

The rule for Phase 0: scaling from Corn-Nano to Corn-Jr should be an edit to a
file in `configs/`, never an edit to code. If a run needs a code change to
change size, the pipeline is not proved yet.
"""

from __future__ import annotations

import importlib.util
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Config:
    # --- identity -----------------------------------------------------------
    name: str = "nano"

    # --- data ---------------------------------------------------------------
    data_dir: str = "data/tinystories"

    # --- initialisation -----------------------------------------------------
    # A checkpoint whose weights this run starts from instead of a fresh init.
    # None is a pretrain. A path is a fine-tune, which DATA.md §10 step 5 needs
    # in order to ask whether the temporal slice has to be *in* pretraining or
    # can be bolted on afterwards. Weights only -- see `train.load_init_weights`
    # for why the optimizer state and the iteration counter stay behind.
    init_from: str | None = None

    # --- tokenizer ----------------------------------------------------------
    # 'byte' is vocab 256 and costs no parameters worth mentioning. A BPE slots
    # in here later; that swap is the experiment that answers the vocab-size
    # question in VISION.md §10.
    tokenizer: str = "byte"

    # --- model --------------------------------------------------------------
    n_layer: int = 6
    n_head: int = 8
    n_embd: int = 256
    block_size: int = 512
    dropout: float = 0.0
    bias: bool = False
    tie_embeddings: bool = True
    # The tag map -- docs/PLAN-LOOP.md §4. A per-token label id, added to the
    # residual stream at the token it labels, so a decision he wrote (the
    # `parts:` line) arrives where the acting layers demonstrably read the
    # label from: blocks 1-3 compute it from the words in a checkpoint that
    # never saw a tag (PLAN-LOOP §1, `scripts/probe_taglayer.py`). 0 means the
    # module is never built and the forward is byte-identical to every
    # checkpoint on disk (`scripts/check_model.py`). 17 is `corn.tagmap.
    # TAG_VOCAB`: a begin and an inside id for each of the eight labels of
    # `corn.grammar.PARSE_LABELS`, plus id 0 for "no tag", which is a zero row
    # that takes no gradient. `tag_layer` is where the map
    # enters: 0 is the embedding sum before block 0 (arm F), k is the residual
    # entering block k (arm H, k = 2 from the rung-0 read).
    tag_vocab: int = 0
    tag_layer: int = 0
    # The structural mask -- docs/PLAN-TAG-SPINE.md §4. True means the
    # dataset carries `train.part.bin` and `train.focus.bin` and every batch
    # is trained under the mask `Batcher` builds from them: a call line may
    # read only the request tokens of the part it executes. Recorded here so
    # a checkpoint says which protocol it was trained under (rule 33) and so
    # `corn/train.py` can refuse a masked model on an unmasked set and the
    # reverse. It changes nothing in the model; the mask arrives per batch.
    attn_structure: bool = False
    # The position encoding -- docs/PLAN-TAG-SPINE.md §5 lever 4, phase C0.
    # "learned" is `wpe`, the absolute table every checkpoint on disk was
    # trained with, and the forward under it is byte-identical to the one
    # before this field existed (`scripts/check_model.py`). "rope" rotates
    # each head's q and k by their position and builds no `wpe` at all, so
    # the attention score depends on the *offset* between two tokens and not
    # on where in the window they sit -- the property the compositional-
    # generalisation literature most consistently finds learned absolute
    # positions lack. Architecture, so `INIT_MUST_MATCH` in `corn/train.py`
    # refuses a fine-tune across it; a checkpoint's own `config.json` says
    # which it is, and one written before the field defaults to "learned".
    pos_enc: str = "learned"
    # RoPE's base wavelength; the standard 10,000 at a 512 block. Read only
    # when `pos_enc == "rope"`.
    rope_theta: float = 10000.0

    # --- optimisation -------------------------------------------------------
    batch_size: int = 32
    grad_accum: int = 1
    max_iters: int = 4000
    lr: float = 1e-3
    min_lr: float = 1e-4
    warmup_iters: int = 100
    # "cosine" is every run in the project to date and stays the default, so a
    # config that does not mention this resolves exactly as it did before the
    # field existed. "wsd" is warmup / stable / decay -- see `corn.train.lr_at`
    # for why the choice has to be made before a long run rather than after.
    lr_schedule: str = "cosine"
    # WSD only: the tail fraction of `max_iters` spent decaying to `min_lr`.
    # 0.1 is the common setting and the one the river-valley analysis reports
    # as near-optimal across budgets; it is a knob here because the right value
    # at 250M has not been measured by anybody in this project.
    decay_frac: float = 0.1
    weight_decay: float = 0.1
    beta1: float = 0.9
    beta2: float = 0.95
    grad_clip: float = 1.0

    # --- eval / logging -----------------------------------------------------
    eval_interval: int = 250
    eval_iters: int = 50
    # Per-source val splits (DATA.md §7) cost this many batches each, on top of
    # the blended figures. Set to 0 to skip them on a multi-source dataset.
    eval_source_iters: int = 20
    log_interval: int = 20

    # --- runtime ------------------------------------------------------------
    device: str = "cuda"
    dtype: str = "bfloat16"  # bfloat16 | float16 | float32
    # On by default since 2026-09-09 (owner: "proven to be only helpful for us
    # time and time again"). Every measurement is a gain -- 1.128x at 20M,
    # 1.07x at 260M, 1.68x on static-shape prefill (finding 64) -- and the
    # old "eager beside eager controls" caution was never measured (finding
    # 124). A config that must train eager sets this False and says why in
    # its docstring. Configs written before this date that omit the field
    # describe checkpoints that trained eager; the checkpoint's own
    # `config.json` is the record of what ran, not this default.
    # PLAN-PARSE-WEIGHTS arm A (7a). `Batcher` samples block offsets uniformly
    # over the token stream, so a block can begin inside a transcript and the
    # `parts:` line at its end is still a loss target -- training a span whose
    # text the window cut off, which is the invented-span species taught
    # directly. Measured on the stream: the utterance is wholly visible for
    # 0.954 of level-1 parse exposures, 0.878 at level 2, 0.788 at level 3 and
    # 0.665 at level 4 in `mix_v3_funcworld_b1024`. With this on, an offset
    # that lands inside a parse-bearing transcript snaps back to that
    # transcript's first token; every such transcript fits a block by
    # construction (`gen_funcworld.py --block`), so nothing is lost and the
    # share of draws that land in the source is unchanged.
    align_parse_blocks: bool = False
    compile: bool = True
    seed: int = 1337
    out_dir: str = "checkpoints"

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.block_size

    @property
    def run_dir(self) -> Path:
        return Path(self.out_dir) / self.name

    def to_dict(self) -> dict:
        return asdict(self)


def load_config(path: str | Path) -> Config:
    """Load a config file that defines a module-level `config = Config(...)`."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"no config at {path}")
    spec = importlib.util.spec_from_file_location(f"corn_config_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "config"):
        raise AttributeError(f"{path} must define a module-level `config = Config(...)`")
    cfg = module.config
    if not isinstance(cfg, Config):
        raise TypeError(f"{path}: `config` must be a Config, got {type(cfg)!r}")
    return cfg


def config_from_dict(d: dict) -> Config:
    """Rebuild a Config from a checkpoint, ignoring fields that no longer exist."""
    known = {f for f in Config.__dataclass_fields__}
    return Config(**{k: v for k, v in d.items() if k in known})
