# PNG validation inputs

Generated locally by `python3 tools/generate_image_fixtures.py` from the repository root;
`--check` verifies the checked-in bytes. No external images or additional dependencies.

Valid fixtures cover RGBA8, indexed color with transparency, grayscale16, Adam7 and an
ancillary text chunk. Invalid fixtures independently change PNG framing, CRC, IHDR order,
palette requirements, trailing bytes and size limits; `animated.png` exercises the static
profile's explicit rejection of APNG. Pixel decoding is exercised separately in the UI Cone.
