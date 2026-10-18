# Validation

Correct key/pedal release distinction, channel separation, tempo changes/rational timing, running status, incomplete captures and ambiguous ordering; reject malformed chunks/VLQs and unsupported timing.

18 behavior test methods plus installed CLI success/finding/malformed cases and byte preservation. CI executes Linux/Python3.10,3.12,3.14 unit, compilation, wheel and clean-venv installed checks. Configured CI alone does not prove success; inspect current Actions results. PREPARATION.json records executed Linux/Python3.12 preparation. Production workloads and other platforms remain untested. No performance benchmark.
