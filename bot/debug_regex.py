#!/usr/bin/env python3
"""Debug regex matching."""
import re
from handlers.commands import handle_health, handle_labs, handle_scores

health = handle_health('/health')
print('=== HEALTH ===')
print(f'Output: {health}')
print(f'Pattern (health|ok|running|items).*\\d: {bool(re.search(r"(?i)(health|ok|running|items).*\d", health))}')
print(f'Pattern \\d{{2,}}: {bool(re.search(r"\d{2,}", health))}')
print()

labs = handle_labs('/labs')
print('=== LABS ===')
print(f'Output (first 300 chars): {labs[:300]}')
print(f'Pattern Lab.{{0,5}}0[1-6]: {bool(re.search(r"(?i)Lab.{0,5}0[1-6]", labs))}')
print(f'Pattern (products|architecture|backend|testing|pipeline|agent): {bool(re.search(r"(?i)(products|architecture|backend|testing|pipeline|agent)", labs))}')
print()

scores = handle_scores('/scores', 'lab-04')
print('=== SCORES lab-04 ===')
print(f'Output (first 400 chars): {scores[:400]}')
print(f'Pattern \\d+\\.?\\d*%: {bool(re.search(r"\d+\.?\d*%", scores))}')
print(f'Pattern \\d+.*attempt: {bool(re.search(r"\d+.*attempt", scores))}')
print(f'Pattern (task|setup|testing|front): {bool(re.search(r"(?i)(task|setup|testing|front)", scores))}')
