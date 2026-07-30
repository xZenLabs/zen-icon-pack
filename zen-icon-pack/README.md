# Zen UI Default Icon Pack

This ZIP is a standalone icon-pack release asset. It is not part of the Zen UI
plugin and does not overwrite bundled Zen UI or KOReader icons.

From the Zen UI repository, build it independently with:

```sh
./icon-packs/build.sh
```

The output is `icon-packs/zen-icon-pack.zip`. Zen UI's normal
build and release workflows do not build or publish this file.

This is a focused, self-contained authoring template for the Zen UI Navbar,
KOReader's top menu tabs, the bottom reader
configuration bar and its controls, highlight/dictionary/lookup actions,
chevrons, dialogs, bookmarks, reading states, and file-manager controls.
Selecting the pack preserves the default appearance.

The pack contains 62 replaceable files from the 2026.07 baseline. It
intentionally excludes unrelated settings, network, and utility artwork.

## Make your own pack

To create a pack, rename the folder and update `id` and `name` in `pack.json`,
then replace any canonical `.svg` files. The folder name and `id`
must match. Unchanged icons may be removed; Zen UI safely falls back per icon.
The `icons` array in `pack.json` is the authoritative list of supported IDs
and exact replacement filenames.

Only those published IDs can replace existing Zen UI or KOReader icons.
Unlisted internal icons remain bundled
and cannot be overridden by a pack. A new, uniquely named icon may still be
added for selection as a custom Navbar tab icon.

For example:

```sh
unzip zen-icon-pack.zip
mv zen-icon-pack my-icon-pack
# Edit my-icon-pack/pack.json and replace icons.
zip -r my-icon-pack.zip my-icon-pack
```

Keep icons at the pack root and preserve their filenames. SVG is preferred;
PNG is also supported. Use transparent artwork that remains legible in black
and white on e-ink screens. A partial pack is valid, so a repository may keep
only the icons it changes.

Copy the folder or ZIP into KOReader's `icons/zen` directory, enable
**Zen UI > Extras > Allow custom icons**, select it under **Custom icon pack**,
and restart KOReader. Zen UI expands a valid ZIP automatically and removes the
ZIP only after installation succeeds.

The selected pack is only an additional first-priority lookup location.
Missing files continue through the normal bundled icon fallbacks.

## Repository contents

- `pack.json` — required pack identity, metadata, and icon filename list.
- `ICON-LIST.md` — every included filename and the UI element it changes.
- Root `.svg` files — replaceable default artwork.
- `LICENSE-ZEN-UI.md` and `LICENSES/` — licenses and attribution to retain when
  redistributing the defaults.

Additional safely named root icons may be added for use in Zen UI's icon
pickers.

Zen UI artwork is covered by `LICENSE-ZEN-UI.md`. KOReader and Material Design
icon attribution and license texts are included in `LICENSES/` in the built
pack.
