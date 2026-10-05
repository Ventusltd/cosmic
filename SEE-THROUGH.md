# See Through: from the whole sky to one substation

*The seer of the cosmic vision sees no enemy, only the play of forces.*

A note left here so the idea and its first working form are recorded beside the telescope they came from.
Written 5 October 2026.

## The idea

The telescope in this repository travels inward: estate, repository, commit, line. Travelling is the zoom, and
nothing is thinned to make the trip easier.

See Through turns the same telescope toward the ground. It starts in the field of stars, every one placed by the
Kuiper rule, and falls without a cut until one real substation fills the view: first the stars, then the stars
gathering into the grid, then the real map, then the real place seen from above, then the place itself standing in
three dimensions with its lines striding away on their towers.

One instrument, one continuous fall, from everything to one thing. A person types the name of a place and is taken
there, and on the way sees that the sky of numbers and the ground under a pylon are the same picture at different
distances.

## What exists

- **A first working form is public** inside Learn the Kuiper:
  https://ventusltd.github.io/kuiper-belt/learn-the-kuiper/ (open MENU, then SEE THROUGH). Source: the
  `learn-the-kuiper` folder of the public `kuiper-belt` repository, file `modules/descent.js`.
  - Type a substation name. Every match lights, and a light on the rim of the circle points to it; with one match
    left it becomes a single beam.
  - GO flies up to the stars (20,000 placed by the real rule), then down as they gather into the substations of
    Great Britain and Northern Ireland (about 5,800, from OpenStreetMap).
  - The circle is a porthole: KUIPER, MAP and SATELLITE are switched inside it, with the scan arm and range rings
    drawn over the real map.
  - GRID and SUBS toggles, as in GridAtlas. It keeps working with no network and says when the real map needs one.
- **The rule underneath is checked.** The placement law used by the stars is the live Kuiper's own line of code; a
  GPU run compared two independent ways of computing it on 1,962,800,054,272 keys with no difference, covering every
  one of the 4,294,967,296 possible directions.

## What comes next

- **See Through as its own app,** ending in three dimensions: the substation drawn by rule from open data (its
  outline, its voltage, the lines that land there, and whatever is mapped inside) standing on the real satellite
  image, with towers rising one after another along the real line routes and the conductors stringing themselves, in
  the manner of the pylon drawing in the Energy Transition Simulator.
- **One rule for every site,** so the same arrival can be played for all 5,800 and more, and for sites not yet
  built.
- **Arrows along real published circuits** between sites, from the grid engine, so the grid can be travelled from
  place to place.
- **The same fall inside a sphere:** the placement rule one dimension up, where the cube root does for volume what
  the square root does for area.

## Its companion: Learn the Kuiper

The same night gave the other half: a screen where one dot is placed anywhere in the circle by typing numbers, so a
person learns the rule by doing it. The four formulas are the ones in the exercise "Build Your Own Kuiper":

    r     = SQRT(k)
    theta = 2 * PI * MOD(k * 2654435769, 4294967296) / 4294967296
    X     = r * COS(theta)
    Y     = r * SIN(theta)

number -> formula -> position. See Through shows where that road ends: at a real place.

## Credits for the public form

Substation names, positions and lines: (c) OpenStreetMap contributors, ODbL. Map: CARTO. Imagery: Esri and its
providers. Map library: MapLibre GL.
