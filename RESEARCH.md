# Research —18 October2026

User: Music editors investigating timing in a small Standard MIDI File.

Pain: Note-off time and sustain release differ; ambiguous simultaneous cross-track events should remain visible.

Smallest useful capability: Explain MIDI key release, CC64 sustain release and exact tempo-derived held-note intervals.

Acceptance: Correct key/pedal release distinction, channel separation, tempo changes/rational timing, running status, incomplete captures and ambiguous ordering; reject malformed chunks/VLQs and unsupported timing.

Demand is inferred from workflow and adjacent public discussions, not verified product requests. Discovery: descriptive GitHub topics, runnable invented example and chronological portfolio index. No unsolicited outreach or activity manipulation.

## Alternatives and evidence

Live GitHub repository search sorted Most stars: `MIDI parser; MIDI Objects`. Highest-star relevant comparable found in the inspected scope: **mido/mido**. Search and reference-follow coverage is limited, not an exhaustive global ranking. Unrelated keyword matches were excluded.

| Repository | Stars observed | Last push UTC | Archived | API license |
| --- | ---: | --- | --- | --- |
| [mido/mido](https://github.com/mido/mido) | 1651 | 2026-09-16T17:16:31Z | False | MIT |
| [craffel/pretty-midi](https://github.com/craffel/pretty-midi) | 1045 | 2026-10-06T20:09:06Z | False | MIT |
| [Tonejs/Midi](https://github.com/Tonejs/Midi) | 1006 | 2023-07-19T09:10:52Z | False | MIT |

Mido already provides full SMF IO. Pretty-midi already has pedal-aware piano-roll processing; Tonejs/Midi already exposes sustain controls. This event evidence view is not the first sustain feature and does not replace these broader libraries.

Current README, selected relevant source and up to five issue/PR records were read. [Provenance](RESEARCH_PROVENANCE.json) preserves exact URLs, observations and source identities. NOASSERTION is unclassified licensing, not permission to copy. No third-party implementation or fixtures are bundled.

Our narrow Python wheel has a clean-install example and failure contract. Established alternatives provide broader workflows, capabilities, documentation, examples and support communities. Competitor installs, time to first useful result, reliability, support response and technical performance were not measured. Our examples prove only our specified behavior. Stars inform discovery, not quality or performance. No feature-absence or superiority claim is made.

Portfolio distinction: The owned CUE/WAVE sample plan partitions source audio frames; PGN clock tooling handles chess labels. This project reconstructs binary musical note/controller state and tempo time, a distinct capability.

Standard formats and algorithms are not inventions of this project; the implementation/report interface and invented fixtures are original. No branding or competitor prose is copied. No technical performance benchmark was conducted.
