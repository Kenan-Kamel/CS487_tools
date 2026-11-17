#!/usr/bin/env bash
# Ground-truth scorecard: compare your findings against the planted bugs.
cat <<'EOF'
╔════════════════════════════════════════════════════════════════╗
║                     GROUND TRUTH (5 bugs)                     ║
╠════╤═══════════════════════════╤══════════════════════════════╣
║  # │ Bug class                 │ Location                     ║
╠════╪═══════════════════════════╪══════════════════════════════╣
║  1 │ Buffer overflow (strcpy)  │ parse_url: strcpy(scheme,..) ║
║  2 │ Format-string vuln        │ print_url: printf(key)       ║
║  3 │ Null-byte injection       │ url_decode: %00 → NUL        ║
║  4 │ Off-by-one / strncpy      │ parse_url else: host[hlen]   ║
║  5 │ Check-then-decode bypass  │ main: is_safe_path before    ║
║    │                           │   url_decode(u.path)         ║
╚════╧═══════════════════════════╧══════════════════════════════╝

Scoring guide:
  5/5  — excellent, you caught everything
  3-4  — solid, most tools miss at least one
  1-2  — typical for a single static analyzer
  0    — try asking an LLM to review the code

Which bugs did each tool find?  Which did only the LLM catch?
EOF
