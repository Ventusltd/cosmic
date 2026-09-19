# cosmic — the telescope

*The seer of the cosmic vision sees no enemy, only the play of forces.*

**37.93 billion lines.** One particle for every line in every file in every commit across 67
repositories, copies counted each time they appear. Nothing is stored, nothing is sampled, and
every number on the instrument came from a command that can fail.

Open `index.html`. Click a body to travel into it, backspace to pull back, drag to steer, scroll
to zoom, `l` for names.

## How to count infinity without being killed by it

Drawing 37.93 billion points onto a million pixels gives roughly forty thousand lines to a pixel.
That is a white flash. It is not a picture of anything, and every pixel is a lie of coverage.

The real sky has the same problem and solves it two ways. Both are copied here exactly.

**Clustering.** Matter is not spread evenly. Stars bind into clusters, clusters into galaxies,
galaxies into superclusters, and between them are voids. The estate is already built the same way
and always was:

    estate  ->  repository  ->  commit  ->  line

Every level is placed by the *same* law as the level above it, so the structure is self-similar
and the black between is structural rather than decorative. **The void is data.** A body is never
allowed a radius larger than a third of the gap to its neighbour, so there is always space
between things, at every level, for any number of children.

**Resolution.** A telescope does not resolve the whole sky at once. Beyond its reach an object is
an unresolved source: you know it is there, you know its brightness, you cannot see inside it. So
a body here is drawn whole, with its line count and its surface brightness stated, until you have
travelled close enough that the screen can hold its lines. Then every one of them is drawn.

The resolving criterion is physics, not taste: **one line per pixel**. Above that the lines
overlap, coverage saturates, and the screen stops carrying information — the same surface
brightness limit that stops a telescope resolving a distant galaxy into stars. Below it,
exclusion holds: every line has a pixel of its own and the count survives the drawing.

You do not see 37.93 billion until you are inside a sector small enough to hold them. Travelling
is the zoom, and nothing is thinned to make the trip easier.

## A universe is a cartridge

The engine knows nothing. It has never heard of git, of wafers or of grids. It is handed
`universe.json` — a hierarchy somebody measured, a named placement law for each level, and the
total those levels must sum to. Swap the cartridge and the same engine draws a CPU, a solar farm
or a network. Nothing in the engine changes.

The cartridge is refused, on screen, if:

- it names a placement law the engine does not have — never quietly substituted with a default
- its top level does not sum to its declared total
- a child level does not sum to its parent

The laws so far:

| law | placement | where it is true |
|---|---|---|
| `areal` | `r = sqrt((i+0.5)/n)`, `theta = i x golden angle` | no preferred axis: gravitational clustering, a repository's commits |
| `grid` | stepper pitch tiled and clipped to the circle, rim steps marked partial | a wafer: a scanner steps a rectangular reticle across a round substrate, and that collision is the geometry |

A wafer drawn on the spiral would be a lie about how silicon is made, which is why the law is the
part that carries the truth and the part a cartridge must declare.

## Travelling must not lose the whole

Zooming is not a view, it is the compute strategy: it collapses the set to what is relevant, which
is the only way to work against something this size. The risk is obvious — you end up holding a
fragment and forgetting the rest exists.

So every unit in the cartridge is in exactly one of three states, every frame:

    resolved  +  held  +  outside the field  =  the whole

The engine computes all three and checks the sum on every frame. If it ever fails, the instrument
prints **MISACCOUNTED** and the amount, and does not pretend otherwise. Travel into globalgrid2050
and the readout says: resolved 0, held 35.56 billion in 5,054 sources, outside 2.37 billion — and
those add to 37.93 billion.

## What the positions mean

**Distance is time.** At every level the centre is the newest work and the rim the oldest, so
travelling outward is travelling backwards. A repository's orbit is its first commit; a commit's
orbit is its own timestamp; a line's radius is its ordinal.

**Area is the share.** A body's radius goes as the square root of its line count, so a body of
twice the area holds twice the lines. Within a level the areas are exactly proportional.

**Across levels nothing is to scale, and it cannot be.** A commit drawn to true scale inside the
estate would be smaller than an atom on this screen. The instrument says so rather than
pretending the zoom is a ruler.

## The measurements

Taken 2026-09-19 by `tools/clusters.py`, walking every path in every commit's tree in every
repository. Run independently the same morning by `tools/belt_split.py`, which produced identical
line and entry totals — two separate walks agreeing to the digit.

| quantity | value | |
|---|---|---|
| every line ever, copies counted | **37,929,011,953** | 37.93 billion |
| file entries ever | 15,065,506 | every path in every commit |
| commits | 9,920 | |
| repositories | 67 | |
| largest body, globalgrid2050 | 35,561,117,636 | 93.8% of the estate |

Earlier the same day, twelve self-hosted runners sharded by content SHA measured the estate at
**37,796,045,093** lines and 14,998,313 entries across **66** repositories. The difference is
+132,966,860 lines, +67,193 entries and one new repository: the estate grew overnight. Both
figures are real and neither replaces the other; the instrument draws the one it loaded and says
which.

Measured by the same runner pass over those 66 repositories, and not re-measured since:

| quantity | value | how |
|---|---|---|
| distinct lines ever recorded | 124,905,502 | every blob in history, deduplicated by content |
| lines present now | 25,335,587 | distinct blobs at HEAD |
| lines added by commits | 57,820,668 | `git log --all --numstat` |
| lines deleted | 11,253,909 | same |
| blobs in history | 42,549 | 40,146 text, 2,403 binary |
| bytes in history | 9,396,220,285 | 8.75 GB |

## How it works

**There is no buffer.** A buffer of 37.93 billion positions would be hundreds of gigabytes. Each
particle's position is computed in the vertex shader from `gl_VertexID` alone. The whole universe
is drawn from a single integer, so nothing is uploaded and nothing can go stale.

**The ordinal does not fit in a float.** At 3.5e10 a float32 step is 4096, so building the ordinal
as a float quantises it and every pass lands on the same positions. The fraction is built from
`float(gl_VertexID)`, exact below 2^24; the angle is built in wrapping `uint` arithmetic, exact
mod 2^32, using the golden angle as the integer ratio 2654435769 / 2^32.

**A sector is fetched only when it is entered.** `belt.tsv` is one row per repository, four
kilobytes. `commits/NN.tsv` is one row per commit, fetched only on entering that repository — 440
kilobytes for the whole estate, and nobody looks at two sectors at once. The page opens in
milliseconds however large the estate becomes.

**It is a long exposure, not an animation.** Nothing moves on a timer; the only motion is your
camera. A resolved body is drawn in interleaved passes so the first lands in milliseconds and
already shows the whole structure, each pass adding detail. Progressive refinement, not sampling:
it converges on the complete set.

**Binary.** A line exists at a position or it does not, so a pixel is lit or it is not. No alpha,
no accumulated brightness, no smoothing. Density shows as coverage, the way a monochrome display
had to do it.

## Three lies this instrument used to tell

Found by opening the page and looking at it, and all three fixed:

**It printed COMPLETE over an empty frame.** The WebGL context was lost to a driver reset; every
draw after that silently did nothing, so the exposure raced to 100% and reported a whole count of
a picture that was never drawn. Context loss is now caught, stated, and stops the exposure.

**It timed the wrong thing.** `drawArrays` returns the moment a command is queued, not when the
GPU has drawn it, so a full exposure was reported in 0.8 seconds when the real figure was minutes.
Every batch now ends in a fence, and the percentage, the seconds and the word COMPLETE all refer
to work the GPU has acknowledged.

**It threw away the exposure it was accumulating.** Without `preserveDrawingBuffer` the browser is
free to discard the drawing buffer after each composite, so every frame but the last was lost
while the instrument went on reporting a long exposure.

A fourth was not a lie but an invention: a minimum orbit radius cleared the centre of every level,
which read as structure and was not in the data. It is gone.

## The addressing

Git has already given every line an address, and this instrument does not invent another:

    <blob sha>:<line>

Content-derived, permanent, identical on every machine that holds that content, allocated by no
authority and never reassignable. `estate-index.tsv` is the routing table —
`sha, lines, repository, commit, path` — which turns an address into a location a reader can open.
It covers 17,599 distinct blobs at HEAD, which is not all of them; the belt is not built from it.

## What it does not claim

It shows **how much**, not **what**. It knows a commit holds 33,214,329 lines; it knows nothing
about what those lines say or whether any of them are any good. Roughly 8.75 GB of the history is
republished data rather than authorship, so **these are lines of text, never "lines of code"**
until that split is measured.

The instrument refuses rather than approximates. If WebGL2 is unavailable it says so instead of
drawing a fraction. If `belt.tsv` does not load it will not invent a sky. If the GPU drops an
exposure it says the count on screen is not complete.

No warranty is given. A chart, not a design.

## Licence

Code under Apache-2.0. Documentation and generated data under CC BY 4.0.
