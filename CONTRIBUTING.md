# Contributing

## Adding attacks (no code required)

Attack payloads live in payloads/owasp_llm.yaml. Add a case under the relevant
category with an id, technique, channel (chat or html), the payload, and an
oracle spec. Supported oracle types are marker, secret, system_prompt, file, and
reflected. The engine and the pytest suite both read this file, so a new payload
is picked up everywhere with no code change.

## Adding a new oracle type

Add the detection function to src/llm_sectest/oracles.py, then register it in the
build_oracle resolver in src/llm_sectest/payloads.py. Keep oracles deterministic
and side-effect free.

## Running the suites
python -m pytest tests/test_owasp_llm.py -v    # requires the vulnerable target running
python -m pytest tests/test_remediation.py -v  # no server needed

## Style

Code targets Python 3.12 and is linted with ruff (line length 100). Run
`ruff check src tests` before opening a pull request. Prefer small, typed
functions and clear names over cleverness.

## Responsible disclosure

This project tests a self-authored vulnerable application. The techniques
generalize; applying them to third-party systems requires explicit
authorization. Do not submit payloads or reports that target systems you do not
own.
