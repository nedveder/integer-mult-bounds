#!/usr/bin/env python3
"""Occam simplicity ledger: an exact check that the selected kappa survives a simpler bit supplier.

Claim checked (finite arithmetic only; inherited premises unchanged):
  replacing the selected record's PR589 bit word (PR555's word plus two tuning moves) by PR555's
  untuned word leaves the selected kappa and all 47 outer strict-constraint values bit-for-bit
  identical, while the word gets 4 fewer gates and needs no tuning search or move list.

Steps
  A. source binding: selected record -> ASSEMBLY.json (sha256), the three pinned exact engines.
  B. complex side: the frozen selected profile, re-rooted by the pinned engine; both exact engines
     sign-check the root interval.  Nothing on the complex side changes.
  C. bit side: both words are replayed exactly (wlib, F2 endpoint on every column); each local paid
     profile, lifted by the frozen nine-stage hosting (288 copies + the same idle remainder), equals
     its own cited pipeline profile; the rank-mass identity and both exact engines (with the bit
     surcharge) reproduce each cited c.
  D. outer assembly: with PR589's c the 47 constraints reproduce ASSEMBLY.json exactly (positive
     control); with PR555's c every constraint value and kappa are identical.
  E. controls: PR543's c (no punctured star) lowers kappa, so the star is load-bearing; a one-unit
     profile mutation breaks the mass identity; the next kappa grid point is rejected.
  F. Occam metric: exact circuit counts and canonical description lengths (see README), compared to
     the committed OCCAM.json.

Standard library only.  Prepared by nedveder with Claude Code (Anthropic) assistance; Apache-2.0.
The 7-step outer driver is the one retained in PR1087's independent/price_profile.py (icekylinx).
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import zlib
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
ENG = ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
T16 = ROOT/'research/complex-t16-rare-pattern-exchanges'
P555 = ROOT/'research/e8-bit-p111'
P589 = ROOT/'research/e8-bit-p111-tuned/tune'
P543 = ROOT/'research/complex-rank5-pivots8/inputs/PR543-EXPECTED.json'

# Nine-stage bit hosting (PR510 chain as parameterised for v <= 120): m = 64, W = 2*K*v*T,
# T = 32 replicas, 288 hosted copies of the local paid profile and a frozen idle remainder that
# PR589's fastc.py read off PR555's own hosted audit.  Step C re-derives that it is the remainder
# of BOTH cited pipeline profiles, i.e. the hosting is identical for the two words.
BIT_M, BIT_COPIES = 64, 288
BIT_REMAINDER = {2: 13920, 4: 14208, 6: 14208, 7: 21312, 42: 288}
COMPLEX_M, COMPLEX_W, COMPLEX_DEFICIT = 73, 14336, 5120
ETA = BETA = Q(1, 10**24)
GRID = Q(1, 10**24)


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location('occam_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def load_json(path):
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    return json.loads(raw)


# ---------------------------------------------------------------- exact moments and outer assembly
def moment_signs(M, B, H, m, W, lower, surcharge):
    """Both pinned engines: moment < 1 at `lower`, > 1 one grid step above."""
    rows = []
    for z, accept in [(lower, True), (lower + GRID, False)]:
        lo, hi = M.moment(H, m, W, z, surcharge)
        blo, bhi = B.moment(m, W, list(H.items()), z)
        if surcharge:  # PR559-era exceptional-residue surcharge: 32 m^2 rank-one calls per 10^16 paid calls
            flo, fhi = B.moment(m, W, [(1, 32*m*m*sum(H.values()))], z)
            blo, bhi = blo + flo/10**16, bhi + fhi/10**16
        require((hi < 1 and bhi < 1) if accept else (lo > 1 and blo > 1), 'moment sign at %s' % z)
        rows.append(dict(endpoint=str(z), accept=accept))
    return rows


def outer47(A, c, b):
    """Seven-step balanced bootstrap and the 47 strict constraints (PR1087 independent driver)."""
    s = min(c, (1-BETA)*b) - Q(1, 10**27)
    require(0 < s < c and s < (1-BETA)*b, 'strict common saving')
    a = Q(384599, 10**10)
    for _ in range(7):
        old = a
        a = (1-s)*s + s*old
        gap = min(s-a, 1-a-s, 1-a-s*(1-old), 1-s)
        require(old < a < s < 1-a and gap > 0, 'bootstrap gap')
    q = a*(1-2*ETA)
    ticks = (1-ETA)*q/(1+q)*10**18
    k = Q((ticks.numerator-1)//ticks.denominator, 10**18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6)-Q(51*20161, 25)}}
    result = A.assembly(a, b, bridge, k, eta=ETA, beta=BETA)
    require(len(result['strict_constraints']) == 47, '47 constraints')
    require(all(v > 0 for v in result['strict_constraints'].values()), 'strict constraints')
    try:
        A.assembly(a, b, bridge, k + Q(1, 10**18), eta=ETA, beta=BETA)
    except AssertionError:
        pass
    else:
        require(False, 'next kappa grid point accepted')
    return dict(common_saving=s, kappa=k, binding='bit' if c < (1-BETA)*b else 'complex',
                constraints={n: str(v) for n, v in result['strict_constraints'].items()})


# ---------------------------------------------------------------- Occam metric
def word_counts(w):
    gates = {sec: len(w[sec]) for sec in 'DABC'}
    summands = {sec: sum(len(g[2]) for g in w[sec]) for sec in 'DABC'}
    used = sorted({g[0] for sec in 'DABC' for g in w[sec]})
    return dict(v=w['v'], R=w['R'], registers=2*w['v']+w['R'], gates=gates, total_gates=sum(gates.values()),
                summands=summands, total_summands=sum(summands.values()), frames_used=len(used))


def description(paths):
    """Occam length of frozen inputs: canonical bytes (exact) and DEFLATE-9 bits (MDL proxy)."""
    rows, total_raw, blob = [], 0, b''
    for p in paths:
        data = canon(load_json(p)) if p.suffix in ('.json', '.gz') else p.read_bytes()
        rows.append(dict(path=p.relative_to(ROOT).as_posix(), canonical_bytes=len(data),
                         deflate_bits=8*len(zlib.compress(data, 9))))
        total_raw += len(data)
        blob += data
    return dict(files=rows, canonical_bytes=total_raw, deflate_bits=8*len(zlib.compress(blob, 9)))


def strip(obj):
    """Drop compressor-dependent fields; canonical byte counts stay exact."""
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in ('deflate_bits', 'zlib_runtime')}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


GEN555 = [P555/'code'/n for n in ('gen_p3.py', 'nodeopt.py', 'pwordl.py', 'planio.py')]
GEN589 = [P589/'apply.py', P589/'wlib.py']


def code_bytes(paths):
    """Package-specific generator code (the shared PR493 skeleton is common to both words)."""
    return dict(files=[p.relative_to(ROOT).as_posix() for p in paths], bytes=sum(len(p.read_bytes()) for p in paths))


def main():
    require(__debug__, 'assertions required (the pinned outer engine asserts)')
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--write', action='store_true', help='rewrite OCCAM.json instead of comparing')
    args = ap.parse_args()

    # A. bindings ---------------------------------------------------------------------------------
    record = json.loads((ROOT/'certificates/selected-result.json').read_text())
    cert_path = ROOT/record['certificate']
    require(sha(cert_path) == record['certificate_sha256'], 'selected certificate hash')
    asm = json.loads(cert_path.read_text())
    require(asm['kappa'] == record['kappa'] and asm['binding'] == 'complex', 'selected kappa / binding')
    require(asm['bit_supplier']['pr'] == 589, 'selected bit supplier is PR589')
    for name in ('moment', 'base_two_moment', 'outer'):
        require(sha(ENG/(name+'.py')) == asm['input_sha256']['engines/%s.py' % name], 'engine pin ' + name)
    M, B, A = (module(ENG/(n+'.py'), n) for n in ('moment', 'base_two_moment', 'outer'))
    wlib = module(P589/'wlib.py', 'wlib')
    print('A. selected record, certificate and three exact engines bound')

    # B. complex side (unchanged) ------------------------------------------------------------------
    plan = load_json(T16/'data/PLAN.json')
    H = {int(r): n for r, n in plan['profile'].items()}
    require(H == {int(r): n for r, n in asm['complex_profile'].items()}, 'complex profile = selected')
    require((plan['M'], plan['live'], plan['deficit']) == (COMPLEX_M, COMPLEX_W, COMPLEX_DEFICIT), 'complex m, W')
    require(COMPLEX_M*COMPLEX_W - sum(r*n for r, n in H.items()) == COMPLEX_DEFICIT, 'complex rank deficit')
    b = Q(M.certify(H, COMPLEX_M, COMPLEX_W, False)['lower'])
    require(b == Q(asm['complex_lower']), 'complex root reproduces the selected b')
    moment_signs(M, B, H, COMPLEX_M, COMPLEX_W, b, False)
    print('B. complex b = %s re-rooted; both engines sign-check it' % asm['complex_decimal'])

    # C. bit side: both words, exact replay -> local paid profile -> hosted profile -> c -----------
    bits = {}
    for tag, pkg_expected, word_path in [('PR555', P555/'EXPECTED.json', P555/'data/bitE8mut-p111.json.gz'),
                                         ('PR589', P589/'EXPECTED.json', P589/'bitE8mut-p111-tuned.json.gz')]:
        exp = json.loads(pkg_expected.read_text())
        w = wlib.load(word_path)
        require(hashlib.sha256(wlib.canon(w)).hexdigest() == exp['word']['content_sha256'], tag + ' word hash')
        local = {int(r): n for r, n in wlib.paid(w).items()}   # asserts nesting and every F2 column
        require(local == {int(r): n for r, n in exp['word']['local_histogram'].items()}, tag + ' local profile')
        hosted = {}
        for r, n in local.items():
            hosted[r] = hosted.get(r, 0) + BIT_COPIES*n
        for r, n in BIT_REMAINDER.items():
            hosted[r] = hosted.get(r, 0) + n
        cited = {int(r): n for r, n in exp['nine']['profile'].items()}
        require(hosted == cited, tag + ' hosted profile = 288 x local + frozen remainder')
        W = exp['nine']['bit']['live']
        v, cst = w['v'], sum(exp['word']['copy_ranks'])
        require(W == 2*4*v*32 and BIT_M*W - sum(r*n for r, n in hosted.items()) == 32*(2*4*v - 9*cst),
                tag + ' rank-mass identity T(2Kv - L cst)')
        c = Q(M.certify(hosted, BIT_M, W, True)['lower'])
        require(c == Q(exp['nine']['bit_lower']), tag + ' c reproduces its cited pipeline value')
        moment_signs(M, B, hosted, BIT_M, W, c, True)
        bits[tag] = dict(c=c, local=local, word=w, counts=word_counts(w))
        print('C. %s: local %s -> c = %s (exact replay, both engines)' % (tag, local, exp['nine']['bit_lower_decimal']))
    require(Q(asm['bit_lower']) == bits['PR589']['c'], 'selected bit c is PR589')

    # D. outer assembly ---------------------------------------------------------------------------
    sel = outer47(A, bits['PR589']['c'], b)
    require(str(sel['kappa']) == asm['kappa'], 'positive control: selected kappa')
    require(sel['constraints'] == asm['outer'], 'positive control: all 47 selected constraint values')
    new = outer47(A, bits['PR555']['c'], b)
    require(new['kappa'] == sel['kappa'] and new['constraints'] == sel['constraints'], 'PR555: identical outer')
    require(new['binding'] == 'complex' and new['common_saving'] == sel['common_saving'], 'complex still binds')
    threshold = (1-BETA)*b
    print('D. kappa %s and all 47 constraint values identical with PR555 (complex binds; c threshold %.12g)'
          % (asm['kappa_decimal'], float(threshold)))

    # E. controls ---------------------------------------------------------------------------------
    c543 = Q(json.loads(P543.read_text())['nine']['bit_lower'])
    low = outer47(A, c543, b)
    require(low['binding'] == 'bit' and low['kappa'] < sel['kappa'], 'PR543 (no punctured star) must lower kappa')
    mutant = dict(bits['PR555']['local'])
    mutant[1] -= 1
    mutant[2] += 1
    mass = sum(r*(BIT_COPIES*n) for r, n in mutant.items()) + sum(r*n for r, n in BIT_REMAINDER.items())
    require(BIT_M*28416 - mass != 10272, 'mutated profile must break the mass identity')
    print('E. controls: PR543 c gives kappa %s < selected (bit binds); profile mutation and next grid rejected'
          % low['kappa'])

    # F. Occam metric ----------------------------------------------------------------------------
    base_inputs = [P555/'data/plan-l3.json', P555/'data/punct.json']
    occam = dict(
        schema='occam-ledger/1',
        kappa=asm['kappa'],
        complex_b=str(b), bit_threshold_c=str(threshold),
        suppliers={tag: dict(c=str(bits[tag]['c']), headroom_over_threshold='%.9f' % float(bits[tag]['c']/threshold - 1),
                             local_paid_profile={str(k): n for k, n in bits[tag]['local'].items()},
                             circuit=bits[tag]['counts']) for tag in ('PR555', 'PR589')},
        frozen_inputs=dict(PR555=description(base_inputs),
                           PR589=description(base_inputs + [P589/'moves.json'])),
        searched_parameters=dict(
            PR555=dict(thirds_seed_and_receivers='bound to the frozen hosting: seeds 0/1/2 give R = 446/448/446 > 4v = 444; '
                                                 'seed 552 with default receivers gives R = 442 and another rank mass',
                       block_node_lu_trials='pays rent in gates only: 1 trial keeps the paid profile, +298 gates'),
            PR589=dict(tuning_search='zero kappa rent: two moves raise the non-binding c by 0.0216%, +4 gates')),
        generator_code=dict(PR555=code_bytes(GEN555), PR589=code_bytes(GEN555 + GEN589)),
        complex_top_layer=description([T16/'data/OWNERS.json.gz', T16/'data/PLAN.json', T16/'data/SPEC.json',
                                       T16/'MOVES.json']),
        rent=dict(
            PR589_tuning=dict(kappa_change='0', binding='complex'),
            PR555_punctured_star=dict(kappa_change=str(low['kappa'] - sel['kappa']), control='PR543 R420 c'),
            PR559_native_correction=dict(kappa_change=str(Q(asm['conservative_kappa']) - sel['kappa']),
                                         note='conservative surcharge model; cited from ASSEMBLY.json')),
        zlib_runtime=zlib.ZLIB_RUNTIME_VERSION)
    out = PKG/'OCCAM.json'
    text = json.dumps(occam, indent=1, sort_keys=True) + '\n'
    if args.write:
        out.write_text(text)
    else:
        committed, fresh = json.loads(out.read_text()), json.loads(text)
        if committed['zlib_runtime'] != fresh['zlib_runtime']:   # DEFLATE sizes are informational across zlibs
            committed, fresh = strip(committed), strip(fresh)
        require(committed == fresh, 'OCCAM.json differs from the recomputed metric')
    g555, g589 = bits['PR555']['counts']['total_gates'], bits['PR589']['counts']['total_gates']
    d555, d589 = occam['frozen_inputs']['PR555']['canonical_bytes'], occam['frozen_inputs']['PR589']['canonical_bytes']
    k555, k589 = occam['generator_code']['PR555']['bytes'], occam['generator_code']['PR589']['bytes']
    print('F. Occam: gates %d -> %d, frozen canonical bytes %d -> %d, generator code bytes %d -> %d, tuning search removed'
          % (g589, g555, d589, d555, k589, k555))
    print('PASS_OCCAM_SIMPLER_BIT_SUPPLIER_SAME_KAPPA', asm['kappa_decimal'])


if __name__ == '__main__':
    main()
