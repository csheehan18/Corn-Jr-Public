"""Generate text from a checkpoint.

Usage:
    python -m corn.sample --ckpt checkpoints/nano/ckpt.pt --prompt "Once upon a time"
"""

from __future__ import annotations

import argparse

import torch

from .config import config_from_dict
from .decode import GraphedDecoder
from .model import build_model
from .tokenizer import check_fingerprint, get_tokenizer


DTYPES = {"fp32": torch.float32, "bf16": torch.bfloat16}


def load_checkpoint(path: str, device: str, dtype: str = "fp32"):
    """Every reader of a checkpoint comes through here -- `chat`, `sample`,
    `bench` and `evals` all call it, which is why the vocabulary check lives
    here rather than in each of them.

    **`dtype` is a measurement condition, not an optimisation, and that is why
    it defaults to `fp32`.** Every scorecard, eval row and finding in this
    project was read off a model in fp32; a checkpoint served in bf16 is the
    same weights answering a different question, and a row from one cannot be
    compared with a row from the other. `harness/server.py` reports it in
    `wiring` for exactly the reason it reports `decline` and `copy`.

    **What bf16 does and does not change.** Training ran under bf16 *autocast*
    -- fp32 master weights, bf16 matmuls -- so bf16 matmul precision is the
    regime these weights were fitted in and is not a departure. Casting the
    weights themselves goes further than autocast did: LayerNorm and the
    embedding table move too, which autocast deliberately keeps in fp32. That
    extra step is where the 994 MB -> 497 MB comes from, and it is also the
    part with no training-time precedent, so the two are worth naming
    separately rather than both being called "bf16".

    **The failure mode is behavioural rather than numerical, because every
    decode here is greedy.** Two logits within bf16's 8-bit mantissa can swap
    order under argmax, and one swapped token at position three changes the
    whole rest of the reply -- so the effect is not a slightly worse answer,
    it is occasionally a different one. On the extraction path that can flip a
    window between a grounded span and a refused invention, which presents on
    a scorecard as a model regression and is not one. `corn/extract.py`'s
    checks are unaffected: they run in Python over decoded text, so drift can
    change what he says and cannot make the verification wrong.
    """
    if dtype not in DTYPES:
        raise ValueError(f"dtype must be one of {sorted(DTYPES)}, got {dtype!r}")
    ckpt = torch.load(path, map_location=device, weights_only=False)
    cfg = config_from_dict(ckpt["config"])
    cfg.device = device
    tokenizer = get_tokenizer(cfg.tokenizer)
    check_fingerprint(ckpt.get("tokenizer_fingerprint"), tokenizer, path)
    model = build_model(cfg, ckpt["vocab_size"])
    # Loaded in fp32 and cast after, never stored cast: the file on disk stays
    # the canonical artefact, and `state_dict` shapes are checked against the
    # weights as written rather than against a converted copy.
    model.load_state_dict(ckpt["model"])
    model.to(device).eval()
    if DTYPES[dtype] is not torch.float32:
        model.to(DTYPES[dtype])
    return model, cfg, tokenizer, ckpt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/nano/ckpt.pt")
    ap.add_argument("--prompt", default="Once upon a time")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--no-graph", action="store_true", help="decode without CUDA graphs")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    model, cfg, tokenizer, ckpt = load_checkpoint(args.ckpt, args.device)
    print(f"{args.ckpt}: iter {ckpt['iter']}, val loss {ckpt['val_loss']:.4f}\n")

    ids = tokenizer.encode(args.prompt) or [ord("\n")]
    idx = torch.tensor([ids], dtype=torch.long, device=args.device)

    decoder = GraphedDecoder(
        model,
        args.device,
        use_graph=not args.no_graph,
        temperature=args.temperature,
        top_k=args.top_k,
    )
    for i in range(args.samples):
        new = decoder.generate(idx, args.tokens)
        print(f"--- sample {i + 1} " + "-" * 52)
        print(tokenizer.decode(ids) + tokenizer.decode(new))
        print()


if __name__ == "__main__":
    main()
