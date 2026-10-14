# Occam ledger: a simplicity metric, and a simpler construction with the same κ

**Result.** Swap the selected record's bit supplier, PR589 (PR555's word plus two tuning moves), for PR555's
untuned word. κ stays **exactly 0.001672660197076918**. All 47 outer strict-constraint values stay identical
too, bit for bit. The construction is strictly simpler under the metric below: 4 fewer gates, no move list,
no tuning search and one fewer source PR (#589). It keeps the same obligations. No new bound is claimed.

The donor asked for simplicity and elegance at the same or better κ, not for a larger κ. This package
defines a metric for that and applies it to the selected record (#1094).

## The metric

κ = a/(1+a) with a = min(bit c, complex b). Detail that does not move the binding side buys nothing. The
ledger asks of every component: **does it pay rent in κ, and what does it cost to describe?**

| Coordinate | Definition | Direction |
|---|---|---|
| κ-rent of a component | κ(C) − κ(C with the component ablated to its predecessor), exact | 0 means Occam waste |
| Occam length 𝓛 | canonical bytes (exact) and DEFLATE-9 bits (an MDL upper bound) of the frozen inputs the certificate consumes but does not regenerate, plus package-specific generator code bytes | lower |
| Circuit size | gates and summands of each supplier word | lower |
| Search load | searched parameters/objects (seeds, trial counts, move lists, owner maps) | fewer |
| Obligations | named conditional premises (H1–H5, all-size, hosting, …) | subset |

**Occam order.** C′ ⪯ C when κ(C′) ≥ κ(C), every certificate check passes, Obl(C′) ⊆ Obl(C), and every
other coordinate of C′ is no larger. C′ is *strictly simpler* when at least one of them is strictly smaller.
Generated data is charged once, through the inputs and code that regenerate it. DEFLATE sizes depend on the
zlib version and are informational; the exact comparisons use canonical byte counts.

## Ledger for the selected record

| | selected (#589 bit) | **Occam-simplified (#555 bit)** |
|---|---|---|
| κ / 47 outer constraint values | 0.001672660197076918 | **identical** |
| bit c (nine stages) | 0.001733427039589844 | 0.001733052823330162 |
| bit headroom over the threshold c* = (1−β)b | 3.4596% | 3.4373% |
| bit gates D/A/B/C | 111/2075/712/2574 = 5472 | 111/2073/712/2572 = **5468** |
| frozen bit inputs: canonical bytes (DEFLATE bits) | 11,808 (31,128) | **10,489 (26,176)** |
| package generator code bytes | 33,243 | **27,493** |
| searched components | plan seed, receivers, LU search, tuning search | plan seed, receivers, LU search |
| obligations | H1–H5 and the inherited premises | same |

κ-rent of the components that were tested (exact; the last two rows are cited, not rebuilt here):

| Component | κ-rent | Description cost | Verdict |
|---|---|---|---|
| #589 tuning (2 moves) | **0** (complex binds) | 5,056 DEFLATE bits + generator code | **Occam waste, removed** |
| #555 punctured star (vs #543 R420 c) | 2.156×10⁻⁵ | punct.json + gen_p3 | load-bearing |
| #555 block-node LU search (2000 trials) | 0 in κ; −298 gates | trial count | pays rent in gates, kept |
| #555 plan seed and receivers | needed for the frozen hosting (canonical seeds give R = 446/448 > 444) | ~30 bits | kept |
| #1094 rare-pattern moves (vs #1087) | 5.66×10⁻⁹ | 44,184 DEFLATE bits | load-bearing, thin |
| PR559 native complex correction | 2.85×10⁻¹² | one proof obligation | load-bearing by 2.85×10⁻¹²; not dropped |

**Where the description lives.** The complex top-layer witness takes 6,710,736 DEFLATE bits. Of that,
OWNERS.json (69,120 = 9 × 16 × 480 role placements) takes 6,580,352 bits. This is about **256×** the frozen
bit inputs. Any further elegance gain at fixed κ has to come from the complex owner map, not the bit word.

## Evidence

- `verify.py` (standard library, about 3 s) checks the following:
  - **Bindings.** It binds the selected record, ASSEMBLY.json and the three pinned exact engines.
  - **Complex side.** It re-roots complex b from the frozen profile (m = 73, W = 14,336).
  - **Bit side.** It replays both bit words exactly: nesting, and the F2 endpoint on all columns. Each local
    paid profile, lifted as 288 × local plus the frozen idle remainder, must equal its own cited nine-stage
    profile. This shows the two words share the hosting. The mass identity T(2Kv − L·cst) must hold, and both
    exact engines (with the bit surcharge) must reproduce each cited c.
  - **Positive control.** PR589's c must reproduce all 47 selected constraint values and κ exactly.
  - **The claim.** PR555's c must give identical values.
  - **Failure controls.** PR543's c makes the bit side bind and lowers κ. A one-unit profile mutation breaks
    the mass identity. The next κ grid point is rejected.
- `regenerate.py` (numpy, about 19 s) rebuilds the shipped PR555 word. It then measures the rent of its
  searched parameters (rows 3–4 of the rent table).
- **Cold replay.** `bash research/e8-bit-p111/verify.sh` passed on this base in 387 s (Python 3.13.16, g++ 13.3,
  Boost 1.83). It confirmed the word, xcheck, the H1–H5 lemma with its mutants, the official cohort
  checkers, nine-stage hosting rediscovery and c = 0.001733052823330162099157.

## Reproduce

```sh
python3 -B research/occam-simplicity-ledger/verify.py          # PASS_OCCAM_SIMPLER_BIT_SUPPLIER_SAME_KAPPA
python3 -B research/occam-simplicity-ledger/regenerate.py      # needs numpy; PASS_OCCAM_SEARCH_RENT
python3 scripts/research_package.py --package research/occam-simplicity-ledger --check-only
# optional cold bit replay (C++17 + Boost headers, ~7 min):
bash research/e8-bit-p111/verify.sh /fresh/dir
```

## Scope and limitations

- This is a finite composition check under the selected record's inherited premises. Those are all-size
  compiler, common-label/mutable-source, whole-call hosting, precision/tape and analytic transfer, plus the
  bit H1–H5 lemma (PR543/PR555 interleaving, still needed). It is not a theorem and not a Lean proof.
- The complex side is reused unchanged. Its full T16 admission was not re-run here.
- The bit side reuses PR555's merged pipeline value, cold-replayed above. The selected record is **not**
  changed: adopting the swap is a maintainer decision.
- The Occam length is a proxy (an MDL upper bound from DEFLATE over canonical JSON). Redundant stored fields
  inflate it. In OWNERS.json, for example, family is a function of (child, copy) and port is a function of
  copy. Compare constructions under the same canonicalization.
- The rent of #1094 and of the native correction is cited from the selected/checkpoint receipts. Only the
  bit rows were recomputed.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. **Structured owner map.** Can a short rule with the same idle profile replace the complex owner map,
   which is about 98% of the description? First step: measure replica/stage periodicity and try a
   deterministic first-fit rule on the T16 windows, checking the profile only. Blocked by the strict T16
   admission chain (PR1018/PR1005 local replay).
2. **Dropping H1–H5.** Can the 3.44% bit headroom buy an H1–H5-free bit word? PR545's punctured R489 word
   passes PR493's interface, but R = 489 > 4v needs a banked nine-stage path.
3. **Search-free plan seed.** Is there a word without a searched seed? Seed 552 with default receivers gives
   R = 442 ≤ 444. Re-host it and price it.

## Related work

[bit589-frame-optimum](../bit589-frame-optimum/README.md) and
[bit589-width-packing](../bit589-width-packing/README.md) study whether PR589's bit c can be raised. Both say
κ is unchanged and complex-bound. This package runs the other way: it gives some of that unused bit headroom
back in exchange for a simpler description. No code or data from them is used.

## Credit

Bit word: eumemic (PR555, on PR543's R420 skeleton and DreamingOfClouds' PR545 punctured star). Tuning
moves and `wlib.py`/`fastc.py`: PR589. The selected complex construction and its lineage are credited in
`docs/research/community-batch1099-review.md` (Rohan Arun's #1094 and predecessors). The pinned exact
engines and outer assembly are by eumemic, icekylinx and Zhihao Chen, as noted in their headers. The 7-step
outer driver follows PR1087's `independent/price_profile.py`. Prepared by nedveder (Nadav Leder) with
substantial Claude Code (Anthropic) assistance. New material Apache-2.0.
