# Icon filename reference

Replace a file at the pack root while keeping the filename exactly as shown.
SVG is preferred. A PNG may be used instead by keeping the same stem, for
example `appbar.menu.png`; when both exist, Zen UI uses the SVG.

The tables below list all 62 files in this focused example pack. Files may be
removed to create a partial pack; Zen UI falls back to its bundled artwork for
anything missing.

## Zen UI Navbar

| Filename | What it changes |
| --- | --- |
| `book.opened.svg` | Continue-reading tab. |
| `home.svg` | Zen UI Home tab. |
| `library.svg` | Library/Books tab. |
| `star.empty.svg` | Favorites tab. |
| `tab_authors.svg` | Authors tab. |
| `tab_collections.svg` | Collections tab. |
| `tab_exit.svg` | Exit tab. |
| `tab_history.svg` | History tab. |
| `tab_left.svg` | Previous-page Navbar control. |
| `tab_manga.svg` | Manga tab. |
| `tab_news.svg` | News tab. |
| `tab_right.svg` | Next-page Navbar control. |
| `tab_series.svg` | Series tab. |
| `tab_stats.svg` | Statistics tab. |
| `tab_tags.svg` | Tags tab. |
| `tab_to_be_read.svg` | To Be Read tab. |

The Navbar Search and Menu tabs use `appbar.search.svg` and
`appbar.menu.svg`, listed with the KOReader top menu below.

## KOReader top menu

| Filename | What it changes |
| --- | --- |
| `appbar.filebrowser.svg` | File browser tab in the reader top menu. |
| `appbar.menu.svg` | Main/more tab in KOReader menus and the Zen UI Navbar Menu tab. |
| `appbar.navigation.svg` | Reader navigation tab. |
| `appbar.search.svg` | Search tab and search actions, including the Zen UI Navbar Search tab. |
| `appbar.settings.svg` | Reader and file-manager settings tab; also shared by the bottom reader menu. |
| `appbar.tools.svg` | Tools tab. |
| `appbar.typeset.svg` | Reader typesetting tab. |

## Reader bottom menu bar

| Filename | What it changes |
| --- | --- |
| `appbar.contrast.svg` | Contrast tab. |
| `appbar.crop.svg` | Page-crop tab. |
| `appbar.pagefit.svg` | Page-fit tab for fixed-layout documents. |
| `appbar.pageview.svg` | Page-view tab. |
| `appbar.rotation.svg` | Screen-rotation tab. |
| `appbar.textsize.svg` | Font/text-size tab. |

The bottom menu Settings tab uses `appbar.settings.svg`, listed above.

## Highlight, dictionary, and lookup actions

| Filename | What it changes |
| --- | --- |
| `lookup.ai.svg` | AI lookup action. |
| `lookup.dictionary.svg` | Dictionary action in the highlight menu. |
| `lookup.highlight.svg` | Add or edit highlight action. |
| `lookup.search.svg` | Search-for-selection action. |
| `lookup.translate.svg` | Translate-selection action. |
| `lookup.vocab.svg` | Add-to-vocabulary action. |
| `lookup.vocab_remove.svg` | Remove-from-vocabulary action. |
| `lookup.wikipedia.svg` | Wikipedia lookup action. |

## Shared reader and menu controls

| Filename | What it changes |
| --- | --- |
| `appbar.pokeball.svg` | Reader long-hold/page-turn state indicator. |
| `back.top.svg` | Back/up control in left-to-right layouts. |
| `back.top.rtl.svg` | Mirrored Back/up control in right-to-left layouts. |
| `bookmark.svg` | KOReader bookmark action and reader bookmark indicator. |
| `cancel.svg` | Cancel control in menu footers. |
| `check.svg` | Confirm and selected-mode control. |
| `chevron.first.svg` | Jump-to-first control. |
| `chevron.last.svg` | Jump-to-last control. |
| `chevron.left.svg` | Previous/back control, including dictionary and reader navigation. |
| `chevron.right.svg` | Next/forward control, including dictionary and reader navigation. |
| `chevron.up.svg` | Expand or return-to-top menu control. |
| `close.svg` | Close control in reader, dictionary, and dialog title bars. |
| `control.collapse.svg` | Collapse a table-of-contents branch. |
| `control.expand.svg` | Expand a table-of-contents branch. |
| `control.expand.alpha.svg` | Transparent reader expansion indicator. |
| `cre.render.partial.svg` | Partial-rendering reader state. |
| `dogear.alpha.svg` | Reader bookmark dog-ear overlay. |
| `edit.svg` | Edit action, including dictionary lookup text. |
| `exit.svg` | Exit/close footer action. |
| `notice-warning.svg` | Warning and error dialogs. |
| `plus.svg` | KOReader Add/new-item action. |
| `position.marker.svg` | Initial-position marker on a reading progress bar. |
| `position.marker.top.svg` | Top-position variant of the reading progress marker. |
| `star.full.svg` | Filled favorite/rating/status star. |
| `texture-box.svg` | Highlight/selection texture indicator. |

For the machine-readable ID-to-filename list, see the `icons` array in
`pack.json`.
