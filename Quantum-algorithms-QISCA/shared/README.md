# Shared Manim Helpers

`quantum_circuit.py` contains reusable primitives for drawing quantum circuits in Manim decks.

Use it for standard gate boxes (`H`, Pauli `X/Y/Z`, `S`, `T`), wire bundles, measurement gates, SWAP, and controlled-SWAP. Lecture files should decide layout and animation timing; the shared module should decide how common circuit symbols look.

Typical use from a lecture folder:

```python
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.quantum_circuit import h_gate, measurement_gate, wire_bundle
```

