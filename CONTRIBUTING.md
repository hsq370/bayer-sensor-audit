# Contributing

Bug reports and small, focused pull requests are welcome. Please include the Python version, operating system, exact command, and a small synthetic input that reproduces a problem. Do not attach patient, clinical, or otherwise private RAW captures to an issue.

For code changes:

1. Install the development dependencies with `python -m pip install -e ".[dev]"`.
2. Add or update a test that checks the expected result on a known array.
3. Run `python -m pytest` and include the result in the pull request.
4. Document any assumptions about CFA order, file metadata, or noise statistics.

New file-format support should require explicit decoding metadata rather than guessing image dimensions, bit packing, byte order, black level, or sensor settings.
