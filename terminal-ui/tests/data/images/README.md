# CPU PNG decode inputs

Generated locally by `python3 tools/generate_image_fixtures.py` from the repository root;
`--check` verifies the checked-in bytes. `.pixels` files contain expected straight-alpha
RGBA8, including partial alpha and zero-alpha pixels. The suite includes palette conversion,
16-bit grayscale and every Adam7 pass without opening a window.

`truncated-deflate.png`, `short-pixels.png` and `bad-filter.png` have valid headers, chunk CRCs
and IEND. Their pixel streams respectively lack compressed bytes, lack a scanline or contain
an invalid filter. They must fail in the actual codec; header validation alone cannot reject
them. The underlying complete-image fix is Scoop PR #226.
