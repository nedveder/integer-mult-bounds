#!/usr/bin/env python3
"""Which searched parameters of PR555's bit word pay rent?  Regenerates the word from its frozen plan.

1. Positive control: the shipped parameters (2000 block-node LU trials) rebuild the shipped word.
2. Block-node search: with ONE LU trial the local paid profile (hence c and kappa) is unchanged, but
   the word has 149 more B gates and 149 more C gates.  The search pays rent in circuit size only;
   it is kept, because the Occam order counts gates.
3. Plan seed and receivers: the canonical seeds 0, 1, 2 (default receivers) give R = 446, 448, 446,
   past the nine-stage whole-hosting wall R <= 4v = 444; seed 552 with default receivers gives R = 442
   and a different rank mass, so the frozen hosting and the c pinned by verify.py do not apply.
   These searched parameters are load-bearing for the frozen hosting (re-hosting R = 442 is open).

Needs numpy (PR493's E8 skeleton).  Prepared by nedveder with Claude Code (Anthropic) assistance; Apache-2.0.
"""
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P555 = ROOT/'research/e8-bit-p111'
SHIPPED = json.loads((P555/'EXPECTED.json').read_text())['word']
WALL = 4*SHIPPED['v']          # nine-stage whole-residual hosting needs R <= 4v


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


sys.path.insert(0, str(P555/'code'))
import gen_p3  # noqa: E402  (inserts PR493's skeleton path itself)

spec = importlib.util.spec_from_file_location('wlib', ROOT/'research/e8-bit-p111-tuned/tune/wlib.py')
wlib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wlib)
plan = str(P555/'data/plan-l3.json')
params = json.loads((P555/'data/punct.json').read_text())
P = sorted(params['punctured'])
shipped_receivers = {int(k): v for k, v in params['receivers'].items()}


def build(seed, receivers, trials):
    gen_p3.NODEOPT[0] = trials
    (_, word), _ = gen_p3.make(plan, P, seed=seed, rcvsel=receivers)
    with tempfile.TemporaryDirectory() as tmp:   # round-trip through the generator's own writer
        gen_p3.save(word, tmp + '/w.json.gz')
        return wlib.load(tmp + '/w.json.gz')


def gates(word):
    return sum(len(word[s]) for s in 'DABC')


w = build(params['thirds_seed'], shipped_receivers, params['nodeopt'])
require(hashlib.sha256(wlib.canon(w)).hexdigest() == SHIPPED['content_sha256'], 'shipped parameters rebuild the word')
paid = wlib.paid(w)
print('1. shipped parameters (%d LU trials) rebuild the shipped word; %d gates' % (params['nodeopt'], gates(w)))

one = build(params['thirds_seed'], shipped_receivers, 1)
require(wlib.paid(one) == paid and one['R'] == w['R'], 'one LU trial keeps the local paid profile')
extra = {s: len(one[s]) - len(w[s]) for s in 'DABC'}
require(extra == {'D': 0, 'A': 0, 'B': 149, 'C': 149}, 'one LU trial costs 149 B and 149 C gates')
print('2. one LU trial: same paid profile %s, +%d gates %s -> search pays rent in gates, not kappa'
      % (dict(paid), sum(extra.values()), extra))

mass = sum(r*n for r, n in paid.items())
for seed in (0, 1, 2, params['thirds_seed']):
    v = build(seed, None, params['nodeopt'])
    vmass = sum(r*n for r, n in wlib.paid(v).items())
    require(v['R'] > WALL or vmass != mass, 'canonical control unexpectedly keeps the hosting')
    print('3. seed %d, default receivers: R = %d (%s the R <= %d wall), rank mass %d vs %d -> not reusable with the frozen hosting'
          % (seed, v['R'], 'inside' if v['R'] <= WALL else 'past', WALL, vmass, mass))
print('PASS_OCCAM_SEARCH_RENT LU search pays in gates; plan seed and receivers bound to the frozen hosting')
