#!/usr/bin/env python3
"""tools/wafer.py - a 300 mm wafer as real geometry, computed from stated inputs.

THE WAFER IS NOT A CLOUD OF DOTS. A scanner steps a rectangular reticle across a round substrate
at a fixed pitch, and the collision between the square step and the circle is the entire geometry
of a wafer map: full fields in the middle, partial fields at the rim that are printed and thrown
away, and an exclusion ring where nothing is printed at all. Drawing that as a spiral of points
would discard the only structure an engineer needs.

So this does not invent a placement law. It computes the actual step positions and writes them as
coordinates, and the engine is told to use them exactly (the `explicit` law). Every number below
is an input you can change or dispute, and the arithmetic is reproducible:

  wafer diameter        300 mm          SEMI M1
  edge exclusion        3 mm            the fixed quality area; 2 mm and 1.5 mm are also used
  reticle field         26 x 33 mm      the scanner slit and scan length, the maximum full field
  scribe lane           0.08 mm         kerf between adjacent dies

Nothing here is measured from a real lot. It is geometry from the standards, and the cartridge
says so, because a computed number and a measured number must never wear the same clothes.

Writes:
  wafer/dies.tsv    label  value_um2  kind  x_mm  y_mm  w_mm  h_mm
  wafer.json        the cartridge

value is AREA IN SQUARE MICROMETRES, which is additive, checkable, and happens to put a 300 mm
wafer within sight of the estate's 37.93 billion lines.
"""
import argparse
import json
import math
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--diameter', type=float, default=300.0, help='wafer diameter, mm')
    ap.add_argument('--exclusion', type=float, default=3.0, help='edge exclusion, mm')
    ap.add_argument('--die-w', type=float, default=26.0, help='die width, mm')
    ap.add_argument('--die-h', type=float, default=33.0, help='die height, mm')
    ap.add_argument('--scribe', type=float, default=0.08, help='scribe lane, mm')
    ap.add_argument('--out', default='.')
    a = ap.parse_args()

    R = a.diameter / 2.0
    Ru = R - a.exclusion                      # the usable radius, inside the exclusion ring
    px, py = a.die_w + a.scribe, a.die_h + a.scribe    # the stepper pitch

    ncx = int(math.ceil(2 * R / px)) + 2
    ncy = int(math.ceil(2 * R / py)) + 2

    rows, full, partial = [], 0, 0
    for iy in range(-ncy, ncy + 1):
        for ix in range(-ncx, ncx + 1):
            cx, cy = ix * px, iy * py          # a centred grid: one step sits on the wafer centre
            # the four corners decide it. All inside the usable circle -> a full field. Some in,
            # some out -> printed but not usable. None in -> the scanner never goes there.
            corners = [(cx - a.die_w/2, cy - a.die_h/2), (cx + a.die_w/2, cy - a.die_h/2),
                       (cx - a.die_w/2, cy + a.die_h/2), (cx + a.die_w/2, cy + a.die_h/2)]
            d = [math.hypot(x, y) for x, y in corners]
            if min(d) > Ru:
                continue                        # not printed at all
            kind = 'full' if max(d) <= Ru else 'partial'
            if kind == 'full':
                full += 1
                area = a.die_w * a.die_h
            else:
                partial += 1
                # A PARTIAL FIELD IS NOT A WHOLE DIE OF SILICON. The reticle is exposed in full,
                # but most of that rectangle hangs off the substrate, so counting it whole makes
                # the printed area exceed the wafer, which is impossible. This is the actual
                # rectangle-circle intersection, on a deterministic sub grid so it reproduces.
                N = 240
                inside = 0
                for sy in range(N):
                    yy = cy - a.die_h/2 + (sy + 0.5) * a.die_h / N
                    for sx in range(N):
                        xx = cx - a.die_w/2 + (sx + 0.5) * a.die_w / N
                        if xx*xx + yy*yy <= Ru*Ru:
                            inside += 1
                area = a.die_w * a.die_h * inside / (N * N)
            rows.append({'label': 'die %+d%+d' % (ix, iy),
                         'value': int(round(area * 1e6)),
                         'kind': kind, 'x': cx, 'y': cy, 'w': a.die_w, 'h': a.die_h,
                         'r': math.hypot(cx, cy)})

    # centre outwards, so that here too distance is the ordering and the newest idea, the centre
    # of the wafer where yield is highest, is where you arrive
    rows.sort(key=lambda r: (r['r'], r['label']))

    os.makedirs(os.path.join(a.out, 'wafer'), exist_ok=True)
    with open(os.path.join(a.out, 'wafer', 'dies.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# label\tvalue_um2\tkind\tx_mm\ty_mm\tw_mm\th_mm\n')
        for r in rows:
            f.write('%s\t%d\t%s\t%.4f\t%.4f\t%.4f\t%.4f\n'
                    % (r['label'], r['value'], r['kind'], r['x'], r['y'], r['w'], r['h']))

    printed = sum(r['value'] for r in rows)
    wafer_area = int(round(math.pi * R * R * 1e6))
    usable_area = int(round(math.pi * Ru * Ru * 1e6))
    good = sum(r['value'] for r in rows if r['kind'] == 'full')

    cart = {
        '_': 'A WAFER IS NOT A SKY. Every level here declares its own law and its own view, so '
             'arriving at a wafer gives you a wafer: an orthogonal stepper grid clipped to a round '
             'substrate, with the partial fields at the rim drawn and counted rather than quietly '
             'dropped. The engine is the same one that draws 37.93 billion lines of git.',
        'name': '300 mm wafer',
        'subtitle': 'computed geometry from the standards, not a measured lot',
        'unit': 'square micrometres',
        'total': printed,
        'provenance': 'computed',
        'computed_by': 'tools/wafer.py, from stated inputs; no lot was measured',
        'inputs': {
            'wafer_diameter_mm': a.diameter, 'edge_exclusion_mm': a.exclusion,
            'die_mm': [a.die_w, a.die_h], 'scribe_mm': a.scribe,
            'stepper_pitch_mm': [round(px, 4), round(py, 4)]
        },
        'derived': {
            'wafer_area_um2': wafer_area,
            'usable_area_um2': usable_area,
            'silicon_under_printed_fields_um2': printed,
            'checks': {
                '_': 'the printed silicon cannot exceed the usable area, and does not',
                'printed_le_usable': bool(printed <= usable_area)
            },
            'full_fields': full,
            'partial_fields': partial,
            'gross_die_per_wafer': full,
            'utilisation_of_wafer': round(good / wafer_area * 100, 2),
            'printed_and_discarded_um2': printed - good
        },
        'extent_mm': R,
        'levels': [{
            'name': 'die', 'plural': 'dies',
            'law': 'explicit', 'view': 'section',
            'source': 'wafer/dies.tsv',
            'columns': ['label', 'value', 'kind', 'x', 'y', 'w', 'h'],
            'child': None,
            '_': 'positions are DATA, not a placement law. A stepper put them there.'
        }],
        'leaf': {'name': 'square micrometre', 'plural': 'square micrometres'},
        'laws': {
            'explicit': 'x, y, w, h come from the measurement. The engine places nothing.',
            'areal': 'r = sqrt((i+0.5)/n), theta = i * golden angle. For things with no preferred axis.'
        },
        'views': {
            'section': 'an engineering section: outlines, a hard grid, the exclusion ring and the '
                       'notch drawn, partial fields dashed. Lines, not dots.',
            'field': 'a population of points, binary, coverage as density. The sky.'
        }
    }
    with open(os.path.join(a.out, 'wafer.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(cart, f, indent=1)

    print(json.dumps({'full_fields': full, 'partial_fields': partial,
                      'printed_um2': printed, 'wafer_area_um2': wafer_area,
                      'utilisation_pct': cart['derived']['utilisation_of_wafer'],
                      'pitch_mm': [round(px, 4), round(py, 4)]}, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
