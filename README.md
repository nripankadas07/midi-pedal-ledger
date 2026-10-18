# midi-pedal-ledger

Explain MIDI key release, CC64 sustain release and exact tempo-derived held-note intervals.

For: Music editors investigating timing in a small Standard MIDI File. Note-off time and sustain release differ; ambiguous simultaneous cross-track events should remain visible.

## Quickstart

Python3.10+; no runtime packages/network. Building the wheel needs setuptools from the normal Python registry.

```sh
git clone https://github.com/nripankadas07/midi-pedal-ledger.git
cd midi-pedal-ledger
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/midi-pedal-ledger --make-example example.mid
.venv/bin/midi-pedal-ledger example.mid
```

Generator creates a new invented MIDI file and refuses overwrite. The report exits0: key-off tick480, CC64 release tick960, held time1000000 microseconds and peak one held voice.

Windows equivalents use `.venv\Scripts\python.exe` and `.venv\Scripts\midi-pedal-ledger.exe`; Windows/macOS have not been executed by this release's Linux CI.

## Contract

Binary SMF formats0/1 with PPQ timing. Running channel status is cleared by meta/sysex. Format1 tempo must be in track0; default is500000 microseconds/quarter. Tempo integration uses exact rational arithmetic; microseconds are integer or numerator/denominator strings. CC64>=64 holds released keys until pedal up. Pedal state is per channel. Events serialize by tick,track,event index; same-channel simultaneous events across tracks are flagged. Unmatched offs and capture-end closures are findings, never fabricated observed releases. Re-striking a pitch while a prior voice is pedal-held is supported; overlapping key-down of identical channel/pitch is refused.

Report JSON goes to stdout. Exit0 means a valid report without documented findings, exit1 a valid report with findings, exit2 invalid/unsupported input or I/O failure with stderr and no partial report. This is a bounded read-only inspection tool; the optional example generator only creates an explicitly named new file.

## Limits

1 MiB,16 tracks,50000 events,20000 notes,maximum tick1e9,PPQ1..32767. Four-byte VLQ maximum. No format2/SMPTE, audible synthesis, other-controller interpretation or physical sounding-duration claims. Channel-mode/reset/all-notes-off controllers are rejected. Other meta/channel events and sysex are counted/ignored. Findings cap512, cross-track evidence256.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/midi-pedal-ledger-check
/tmp/midi-pedal-ledger-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/midi-pedal-ledger-check/bin/python
```

Installed-command checks run outside the checkout. See [validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md), [security](SECURITY.md) and [license](LICENSE).

Original implementation, prose and invented fixtures developed with AI assistance. MIT license. No verified production adoption or performance-superiority claim.
