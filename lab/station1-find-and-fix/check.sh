#!/bin/sh
# Run every input through the sanitizer build and report.
# A "fixed" recparse must: handle good.bin, reject the bad files without a
# sanitizer report, and never print bytes from the data field as the name.
cd "$(dirname "$0")"
fail=0
for f in inputs/*.bin; do
    out=$(ASAN_OPTIONS=detect_leaks=0 ./recparse-asan "$f" 2>&1); rc=$?
    if echo "$out" | grep -q "Sanitizer"; then
        printf '%-24s \033[31mFAIL\033[0m  sanitizer report\n' "$f"; fail=1
    elif [ $rc -ne 0 ]; then
        printf '%-24s \033[31mFAIL\033[0m  crashed (exit %d)\n' "$f" $rc; fail=1
    elif [ "$f" = inputs/good.bin ] && ! echo "$out" | grep -q "2 record(s)"; then
        printf '%-24s \033[31mFAIL\033[0m  good.bin must still parse 2 records\n' "$f"; fail=1
    elif [ "$f" = inputs/leak-name32.bin ] && echo "$out" | grep -q 'name="B*SECRET'; then
        printf '%-24s \033[31mFAIL\033[0m  name printed bytes from the data field\n' "$f"; fail=1
    else
        printf '%-24s \033[32mok\033[0m\n' "$f"
    fi
done
exit $fail
