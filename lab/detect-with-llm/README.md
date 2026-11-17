# Station: LLM-assisted bug detection

Compare traditional static analyzers against an LLM code reviewer on a
small C program with planted security bugs.

## Setup

```bash
make          # normal build
make asan     # build with AddressSanitizer
```

You also need **flawfinder** and/or **cppcheck** for the analyzer step:
```bash
pip install flawfinder        # or: apt install flawfinder
apt install cppcheck          # or: brew install cppcheck
```

## Steps

1. **Read the code** — open `urlparse.c` and look for security bugs.
   Write down what you find.

2. **Run the static analyzers** — `bash analyze.sh` runs gcc warnings,
   flawfinder, and cppcheck. Record what they report.

3. **Ask an LLM** — paste `urlparse.c` into Claude (or another LLM) with
   the prompt:

   > Review this C code for security vulnerabilities. List each bug with
   > its location, severity, and how an attacker could exploit it.

   Record the LLM's findings.

4. **Compare** — which bugs did each approach find?

5. **Reveal** — run `bash reveal.sh` to see the ground-truth scorecard.

6. **Exploit** — run `bash exploit.sh` to see each bug triggered with ASan.

## Discussion

- Which bugs are easy for static tools? Which require understanding intent?
- Did the LLM produce any false positives?
- Would you trust the LLM's output without verification?
