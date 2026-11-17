# Station 1 · Find, fix, then break the fix

You get a small C program, `recparse.c`, that parses a binary record file.
It has bugs. Your job is **not** to fix them yourself. Your job is to make
a machine find and fix them, and then decide whether to believe it.

Work in pairs. One laptop drives the agent, the other keeps a terminal
open for verification. Swap halfway.

## 0. Setup (2 min)

```sh
cd lab/station1-find-and-fix
make inputs        # writes inputs/*.bin
make               # builds ./recparse and ./recparse-asan
./check.sh         # runs every input through the sanitizer build
```

You should see three FAIL lines. That is the starting score.

## 1. Static analysis first (5 min)

Run whatever analyzers you have. Two cheap ones that work in the SEED VM:

```sh
sudo apt install -y cppcheck && cppcheck --enable=warning,style recparse.c
pip3 install flawfinder && flawfinder recparse.c
```

If Docker works, Semgrep's community rules:

```sh
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan --config p/c
```

Write down: how many findings, which lines, and how many you think are real.

## 2. Let the agent loose (10 min)

Start Claude Code in this directory and give it the analyzer output:

```
claude
> Here is recparse.c and the output of cppcheck and flawfinder.
> Find every memory-safety bug, fix each one, and explain each fix.
> Do not change the file format or the output format.
```

Watch what it does. Note **which** bugs it reports and **how** it fixes each.

Then compare with the pair next to you. Same bugs? Same patches?

## 3. Verify (5 min)

```sh
make clean && make && ./check.sh
```

All green? Now look at `inputs/leak-name32.bin`. Run the fixed binary on
it and read the printed name carefully:

```sh
./recparse inputs/leak-name32.bin
```

If the name is longer than 32 characters, the patch is *plausible*, not
*correct*. Ask the agent why, and whether its fix handles a name of
exactly 32 bytes. Then run `./check.sh` again.

## 4. Break it (5 min)

`check.sh` is a test suite, not a proof. Write one more input in
`mkinputs.py` that you think the patched program will mishandle. Ideas:

- a record whose `len` field is exactly `MAX_DATA`
- a file that ends in the middle of the 4-byte length
- an empty file, a 1-byte file
- a name with no NUL anywhere in the file

Did you find anything? Did the agent find it when you asked?

## 5. Write down (2 min)

1. How many bugs did the analyzer flag, and how many were real?
2. Did the agent's first patch pass `check.sh`? Did it pass `leak-name32`?
3. Did your neighbor's agent produce the same patch? Same bugs?
4. What test would convince you the program is now correct? Could any
   finite set of tests do that?

Question 4 is the point of the lecture.

---

**Instructor notes:** `solution/recparse-plausible.c` is the strncpy
patch that passes the two crash inputs and still fails `leak-name32`.
`solution/recparse-fixed.c` passes everything. The patches as diffs are
in `solution/*.patch`.
