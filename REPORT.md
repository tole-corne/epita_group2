# TP 2 — Student Report: Modern Python Tooling & Live API Systems

**Student Name / Team:** Group 2  
**EPITA Login:** `epita.group2`  
**Assigned API Group:** Group 6 — Geolocation & IP Ops (IPInfo.io), used following the instructor's direct instruction  
**Date:** 31/10/2026  
**TestPyPI Live Package URL:** https://test.pypi.org/project/epita-group2/

---

## Step 0: Assigned Group Verification

- **Assigned domain:** Group 6 — Geolocation & IP Ops (IPInfo.io), as listed in the Step 0 table of the lab.
- **Endpoint:** `GET https://ipinfo.io/json` with an `Authorization: Bearer <token>` header.
- **Environment variable:** `IPINFO_TOKEN`.
- **Project directory:** `epita_group2` (`C:\Users\hamad\Documents\epita\epita_group2`).
- **Package name:** `epita-group2`.
- **Note:** the lab document does not define a group-verification command, so no command output is included. The group was applied following the instructor's direct instruction.

## Part 1: Environment Isolation with `uv`

### 1. Comparison of `sys.executable` and `sys.prefix`

We initialized the library project using `uv init --lib epita_group2`, created an isolated environment with `uv venv`, and ran `scripts/inspect_env.py` using global Python and `uv run`.

**Global Python environment (`python3 scripts/inspect_env.py`):**

```text
sys.executable: C:\Users\hamad\AppData\Local\Python\pythoncore-3.15-64\python.exe
sys.prefix: C:\Users\hamad\AppData\Local\Python\pythoncore-3.15-64
sys.base_prefix: C:\Users\hamad\AppData\Local\Python\pythoncore-3.15-64
Python version: 3.15.1
Is in Virtual Environment? False
```

**Isolated project environment (`uv run python scripts/inspect_env.py`):**

```text
sys.executable: C:\Users\hamad\Documents\epita\epita_group2\.venv\Scripts\python.exe
sys.prefix: C:\Users\hamad\Documents\epita\epita_group2\.venv
sys.base_prefix: C:\Users\hamad\AppData\Local\Python\pythoncore-3.15-64
Python version: 3.15.1
Is in Virtual Environment? True
```

**Analysis:** Global Python uses the system installation for `sys.executable` and `sys.prefix`. In contrast, `uv run` starts the project's `.venv` interpreter, so `sys.executable` and `sys.prefix` point inside `.venv`, while `sys.base_prefix` still refers to the underlying global installation. The `uv run` command selects and manages the project environment without requiring manual shell activation. This isolates dependencies between projects and supports reproducible development. Both runs used Python 3.15.1, so the difference was environment isolation rather than Python version.

**Git configuration:** `.gitignore` includes `.venv/`, `.env`, `__pycache__/`, `dist/`, `*.egg-info/`, and `*.txt`. We committed `.gitignore` and `scripts/inspect_env.py` with commit `94b22f6` (`Add gitignore and env inspection script`).

## Part 2: Live API Connection & 12-Factor Secret Hygiene

### 1. Git status and secret configuration

```text
PS> git status
On branch master
nothing to commit, working tree clean
```

We separately verified:

```text
PS> git ls-files .env.template
.env.template

PS> git check-ignore .env
.env
```

This confirms that the public `.env.template` file is tracked and the private `.env` file is ignored. The application reads its credential from the `IPINFO_TOKEN` environment variable through `python-dotenv`. The configuration module validates that the key is present and is not a placeholder before making a request.

### 2. Live API response (redacted)

**Command:**

```powershell
uv run python -c "from epita_group2.client import fetch_live_data; print(fetch_live_data())"
```

**Output (IP address redacted):**

```python
{
    'status': 'LIVE_SUCCESS',
    'ip': '[REDACTED]',
    'city': 'Nootdorp',
    'region': 'South Holland',
    'country': 'NL',
    'org': 'AS199218 Proton AG'
}
```

The client sent a GET request to `https://ipinfo.io/json` with an `Authorization: Bearer` header and returned parsed JSON fields. The `LIVE_SUCCESS` status verifies that the live API request completed successfully.

### 3. Security analysis

**Two reasons why environment variables are superior to configuration files such as `config.json` or `settings.yaml`:**

1. Keeping credentials outside tracked source files reduces the risk of exposing API tokens through commits, shared repositories, or source-code archives. In this project, the `.env` file is explicitly ignored by Git.
2. It separates configuration from application logic. Different environments or deployments can supply different API tokens without changing the Python code.

**Why default secret fallbacks are dangerous:** Using a fallback such as `os.getenv("API_KEY", "default")` can conceal missing configuration and lead the program to use an invalid or unintended credential. Missing or placeholder production secrets should be rejected explicitly rather than silently accepted.

## Part 3: Dependency Hygiene & Semantic Versioning

### 1. Dependency tree (`uv tree`)

```text
epita-group2 v0.1.0
├── python-dotenv v1.2.4
├── requests v2.34.2
│   ├── certifi v2026.10.23
│   ├── charset-normalizer v3.5.2
│   ├── idna v3.20
│   └── urllib3 v2.8.0
├── rich v15.0.0
│   ├── markdown-it-py v4.2.0
│   │   └── mdurl v0.1.2
│   └── pygments v2.21.0
└── pytest v9.2.0 (group: dev)
    ├── colorama v0.4.6
    ├── iniconfig v2.3.1
    ├── packaging v26.3
    ├── pluggy v1.7.0
    └── pygments v2.21.0
```

**Direct runtime dependencies:** `python-dotenv`, `requests`, and `rich`.  
**Direct development dependency:** `pytest` (in the `dev` dependency group).  
**Transitive dependencies of `requests`:** `certifi`, `charset-normalizer`, `idna`, and `urllib3`.  
**Transitive dependencies of `rich`:** `markdown-it-py`, `pygments`, and `mdurl` (through `markdown-it-py`).  
**Development transitive dependencies of `pytest`:** `colorama`, `iniconfig`, `packaging`, `pluggy`, and `pygments`.

### 2. Lockfile and Semantic Versioning analysis

**Version constraints:**

- `requests = "^2.31.0"` is a caret constraint, allowing versions `>=2.31.0` and `<3.0.0`.
- `urllib3 = "~=2.2.1"` is a PEP 440 compatible-release constraint, allowing versions `>=2.2.1` and `<2.3.0`.
- `rich = "==13.7.1"` pins exactly version `13.7.1`.

**Would `^2.31.0` allow an upgrade to `3.0.0`?** No. Major version 3 is outside the permitted range, so `uv lock --upgrade` would not select it under `^2.31.0`. A major upgrade requires explicitly changing the constraint, because major versions may contain breaking changes.

**Difference between `pyproject.toml` and `uv.lock`:** `pyproject.toml` declares the project's metadata, direct dependencies, and permitted version ranges (the declaration). `uv.lock` records the resolved dependency graph with exact package versions and artifact hashes (the pinning), allowing `uv` to reproduce an identical environment. Our project uses constraints such as `requests>=2.34.2` and `rich>=15.0.0`; the caret, tilde, and equality examples above are the assignment's theory scenarios.

**How SHA-256 hashes protect the build:** Hashes in `uv.lock` provide integrity checks for downloaded distributions. A downloaded artifact whose content differs from its recorded hash is rejected, which protects against corrupted downloads and against tampered or substituted packages (supply-chain attacks). Hash verification does not by itself prove that a package or its publisher is trustworthy.

## Part 4: Package Build & TestPyPI Deployment

### 1. TestPyPI deployment details

**Published package:** `epita-group2`  
**Version:** `0.1.0`  
**Public URL:** https://test.pypi.org/project/epita-group2/  
**CLI entry point:** `epita-epita-group2-cli = "epita_group2.cli:main"`

**Build command and output:**

```powershell
uv build
```

```text
Building source distribution...
Building wheel from source distribution...
Successfully built dist\epita_group2-0.1.0.tar.gz
Successfully built dist\epita_group2-0.1.0-py3-none-any.whl
```

**Publish command:**

```powershell
uv publish --publish-url https://test.pypi.org/legacy/ --token "<TESTPYPI_TOKEN>"
```

Both the wheel and the source distribution were uploaded. The token is intentionally omitted.

**Live verification: installation from TestPyPI in a clean temporary directory.** The command was run from `%TEMP%`, outside the project, with `IPINFO_TOKEN` set in the shell:

```powershell
uv run --with epita-group2 --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ epita-epita-group2-cli
```

**Output (IP address redacted):**

```text
╭─────── EPITA Engineering Tools - Session 2 ───────╮
│ Live System Telemetry: LIVE_SUCCESS               │
│ ┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓             │
│ ┃ Property ┃ Value                  ┃             │
│ ┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩             │
│ │ status   │ LIVE_SUCCESS           │             │
│ │ ip       │ [REDACTED]             │             │
│ │ city     │ Naaldwijk              │             │
│ │ region   │ South Holland          │             │
│ │ country  │ NL                     │             │
│ │ org      │ AS49981 WorldStream... │             │
│ └──────────┴────────────────────────┘             │
╰───────────────────────────────────────────────────╯
```

The package installed from TestPyPI (with dependencies resolved from PyPI) and the CLI returned live data, which confirms that the published package works outside the development environment.

### 2. Packaging theory

**Difference between an `sdist` and a Wheel:** A source distribution (`.tar.gz`) contains the project's source and build metadata; installing it may require a build step on the target machine. A Wheel (`.whl`) is a pre-built distribution in a standardized format that an installer can unpack directly for a compatible Python environment.

**Why Wheels are faster and safer to install:** They install faster because nothing has to be built on the user's machine. They are also safer because installing a Wheel does not execute build scripts (`setup.py` or a build backend), which reduces build-time code execution and variability from local compilers or build dependencies. A Wheel is not automatically trustworthy, since its source and integrity still matter.

## Part 5: Professional Debugging Challenge (No `print()` for debugging)

### 1. Root cause analysis

The original `parse_api_record()` function used `.split(",")`, which returns strings. Therefore both `record["volume"]` and `record["weight"]` had the runtime type `str`.

In post-mortem debugging, we inspected:

```text
(Pdb) p volume
'120'
(Pdb) p weight
'2'
(Pdb) p type(volume)
<class 'str'>
```

The program crashed in `compute_weighted_metric()` at `return volume * weight` with:

```text
TypeError: can't multiply sequence by non-int of type 'str'
```

Python cannot multiply two strings. Note that if only `weight` were an integer, the code would not crash but would silently produce a wrong result, because `'120' * 2` repeats the string (`'120120'`). Even if the multiplication were fixed, `total_volume += record["volume"]` would also fail because it adds a string to an integer.

### 2. Conditional breakpoint and call stack

We set a conditional breakpoint on line 32 of `aggregate_telemetry()` (triggering only when `idx == 2`), then stepped into `compute_weighted_metric()`:

```text
(Pdb) b 32, idx == 2
Breakpoint 1 at ...\scripts\debug_challenge.py:32
(Pdb) c
> ...\debug_challenge.py(32)aggregate_telemetry()
-> impact = compute_weighted_metric(record["volume"], record["weight"])
(Pdb) s
--Call--
> ...\debug_challenge.py(19)compute_weighted_metric()
-> def compute_weighted_metric(volume, weight):
(Pdb) where
  ...\bdb.py(912)run()
-> exec(cmd, globals, locals)
  <string>(1)<module>()
  ...\debug_challenge.py(57)<module>()
-> result = aggregate_telemetry(api_payload)
  ...\debug_challenge.py(32)aggregate_telemetry()
-> impact = compute_weighted_metric(record["volume"], record["weight"])
> ...\debug_challenge.py(19)compute_weighted_metric()
-> def compute_weighted_metric(volume, weight):
```

**Call stack frames observed:**

1. `bdb.py` `run()`: the debugger's execution wrapper that launches the script.
2. `<string>` `<module>`: the entry point created by `pdb`.
3. `debug_challenge.py` `<module>`, line 57: calls `aggregate_telemetry(api_payload)`.
4. `aggregate_telemetry()`, line 32: calls `compute_weighted_metric(...)` for the record with `idx == 2`.
5. `compute_weighted_metric()` (current frame, marked `>`): paused at the function entry.

Ignoring the debugger's own two frames, the stack is the expected chain `<module>` → `aggregate_telemetry` → `compute_weighted_metric`.

### 3. The fix

We converted the numerical fields when parsing each record:

```diff
- "volume": parts[2],
+ "volume": float(parts[2]),
  "status": parts[3],
- "weight": parts[4]
+ "weight": int(parts[4])
```

This makes the multiplication and the aggregation numeric.

### 4. Verified execution output

Command run outside the debugger:

```powershell
uv run python scripts/debug_challenge.py
```

```text
Aggregate Result: {'successful_entries': 3, 'total_volume': 650.0, 'avg_volume': 216.66666666666666, 'high_impact_count': 1}
```

This matches the expected values for the three `SUCCESS` records: volumes `120 + 450 + 80 = 650`, average volume `650 / 3 ≈ 216.67`, and one high-impact record (`450 × 3 = 1350`, greater than 500).

