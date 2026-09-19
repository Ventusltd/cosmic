# cosmic — the telescope

*The seer of the cosmic vision sees no enemy, only the play of forces.*

A telescope pointed at everything git has ever recorded. Every line is a particle. Nothing is
stored, nothing is sampled, and every number on the instrument was measured by a command that can
fail.

Open `index.html`. Drag to steer, scroll to zoom, press `d` to change what is counted.

## What it shows

**37,796,045,093 particles.** One for every line in every file in every commit across 66
repositories — copies counted each time they appear, deletions included, nothing left out.

Press `d` and it shows **124,905,502**: the same universe with copies collapsed by content, which is
what git deduplicates to. Both numbers are real. Neither stands for the other, and the instrument
says which one it is drawing.

## The measurements

Taken 2026-09-19 by twelve self-hosted runners, sharded deterministically by content identifier, all
twelve shards present. Every figure is recomputable by anyone with a clone.

| quantity | value | how |
|---|---|---|
| every line ever, copies counted | **37,796,045,093** | every path in every commit's tree |
| distinct lines ever recorded | **124,905,502** | every blob in history, deduplicated by content |
| lines present now | 25,335,587 | distinct blobs at HEAD |
| lines added by commits | 57,820,668 | `git log --all --numstat` |
| lines deleted | 11,253,909 | same |
| file entries ever | 14,998,313 | every path in every commit |
| commits | 9,912 | |
| blobs in history | 42,549 | 40,146 text, 2,403 binary |
| bytes in history | 9,396,220,285 | 8.75 GB |
| repositories | 66 | |

## How it works

**There is no buffer.** A buffer of 37.8 billion positions would be hundreds of gigabytes. Each
particle's position is computed in the vertex shader from `gl_VertexID` alone:

    r = sqrt((k + 0.5) / n)
    theta = k * 2.399963229728653

The whole universe is drawn from a single integer. Nothing is uploaded and nothing is stored, so
nothing can go stale.

**Distance is time, as in the night sky.** Every star you see is a different past arriving in the
same instant: four years for the nearest, millions for a distant galaxy. Looking further out is
looking further back. The instrument obeys the same rule.

**It is a long exposure, not an animation.** No GPU draws 37.8 billion points in one frame, so the
same complete population accumulates across frames without clearing — roughly eighty seconds to a
full exposure, with the progress stated the whole way. Moving the view restarts the exposure,
because re-pointing a telescope starts a new plate. Sixty frames a second is for things you steer.
This is something you look at.

**Binary.** A line either exists at a position or it does not, so a pixel is lit or it is not. No
alpha, no accumulated brightness, no smoothing. Density shows as coverage, the way a monochrome
display had to do it, and it is more truthful as well as simpler.

## The addressing

Git has already given every line an address, and this instrument does not invent another:

    <blob sha>:<line>

Content-derived, permanent, identical on every machine that holds that content, allocated by no
authority and never reassignable. `estate-index.tsv` is the routing table —
`sha, lines, repository, commit, path` — which turns an address into a location a reader can open.

## What it does not claim

It draws lines, not meaning. A particle is a line of text that exists; it is not a statement about
what that line does or whether it is any good. Roughly 8.75 GB of the history is republished data
rather than authorship, so **these are lines of text, never "lines of code"** until that split is
measured.

The instrument refuses rather than approximates. If WebGL2 is unavailable it says so instead of
drawing a fraction. If the drawn count ever fails to equal the total, it prints INCOMPLETE.

No warranty is given. A chart, not a design.

## Licence

Code under Apache-2.0. Documentation and generated data under CC BY 4.0.
