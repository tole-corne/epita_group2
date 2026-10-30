# TP 2 — Student Report: Modern Python Tooling & Live API Systems

**Student Name / Team:** Group 2  
**EPITA Login used for project naming:** `epita.group2`  
**Assigned API Group:** Group 2 — IPInfo implementation (used following the instructor's direct instruction; the distributed group roster originally identifies CryptoCompare for Group 2)  
**Date:** 30/10/2026  
**TestPyPI Live Package URL:** https://test.pypi.org/project/epita-group2/

---

## Step 0: Assigned Group Verification

- **Group:** Group 2 (`group2` in the project name), as shown in the cohort group roster.
- **API used:** IPInfo, `GET https://ipinfo.io/json`, following the instructor's direct instruction.
- **Project directory:** `epita_group2` (`C:\Users\hamad\Documents\epita\epita_group2`).
- **Project login:** `epita.group2` (the login used in the group CLI naming).
- **Package name:** `epita-group2`.
- **Group verification command output:** Not present in the supplied terminal history. The roster identifies our team as Group 2; the terminal history confirms the implementation uses IPInfo.

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

Our final Git check returned:

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

This confirms that the public `.env.template` file is tracked and the private `.env` file is ignored. The working tree was clean when we ran the check. The application reads its credential from the `IPINFO_TOKEN` environment variable through `python-dotenv`. The configuration module validates that the key is present and is not a placeholder before making a request.

### 2. Live API response (redacted)

**Command:**

```powershell
uv run python -c "from epita_group2.client import fetch_live_data; print(fetch_live_data())"
```

**Observed output (IP address redacted):**

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

The client sent a GET request to `https://ipinfo.io/json` with an `Authorization: Bearer` header and returned parsed JSON fields. The `LIVE_SUCCESS` result verifies that the live API request completed successfully.

### 3. Security analysis

**Two benefits of storing secrets in environment variables instead of committed configuration files:**

1. Keeping credentials outside tracked source files reduces the risk of exposing API tokens through commits, shared repositories, or source-code archives. In this project, the `.env` file is explicitly ignored by Git.
2. It separates configuration from application logic. Different environments or deployments can supply different API tokens without changing the Python code.

**Why default secret fallbacks are dangerous:** Using a fallback such as `os.getenv("API_KEY", "default")` can conceal missing configuration and lead the program to use an invalid or unintended credential. Missing or placeholder production secrets should be rejected explicitly rather than silently accepted.

## Part 3: Dependency Hygiene & Semantic Versioning

### 1. Dependency tree (`uv tree`)

**Actual output recorded in PowerShell:**

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

- `requests = "^2.31.0"` is a caret constraint (commonly used in Poetry-style notation), allowing versions `>=2.31.0` and `<3.0.0`.
- `urllib3 = "~=2.2.1"` is a PEP 440 compatible-release constraint, allowing versions `>=2.2.1` and `<2.3.0`.
- `rich = "==13.7.1"` pins exactly version `13.7.1`.

**Would `^2.31.0` allow an upgrade to `3.0.0`?** No. The major version 3 is outside the permitted range, so a dependency resolver should not select it solely under `^2.31.0`, even when updating the lockfile. A new major-version constraint would have to be approved explicitly.

**Difference between `pyproject.toml` and `uv.lock`:** `pyproject.toml` declares the project's metadata, direct dependencies, and permitted version ranges. `uv.lock` records a resolved dependency graph with specific package versions and artifact metadata/hashes, allowing `uv` to reproduce a consistent environment. Our project used constraints such as `requests>=2.34.2` and `rich>=15.0.0`; the caret, tilde, and equality examples above are theory questions from the assignment, not a claim that our project uses those exact constraints.

**How SHA-256 hashes protect the build:** Hashes in `uv.lock` provide integrity checks for downloaded distributions. A downloaded artifact whose content differs from its recorded hash can be detected and rejected, reducing the risk of accidental corruption or artifact substitution. Hash verification does not, by itself, guarantee that a package or its publisher is trustworthy.

## Part 4: Package Build & TestPyPI Deployment

### 1. TestPyPI deployment details

**Published package:** `epita-group2`  
**Version:** `0.1.0`  
**Public URL:** https://test.pypi.org/project/epita-group2/  
**Configured CLI entry point:** `epita-epita-group2-cli = "epita_group2.cli:main"`

**Observed local CLI invocation:**

```powershell
uv run epita-epita-group2-cli
```

**Observed output (IP address redacted; table simplified):**

```text
EPITA Engineering Tools - Session 2
Live System Telemetry: LIVE_SUCCESS

Property  Value
status    LIVE_SUCCESS
ip        [REDACTED]
city      Nootdorp
region    South Holland
country   NL
org       AS199218 Proton AG
```

The command displayed a styled `rich` terminal panel and table. This demonstrates successful **local** CLI execution. The supplied terminal history does not show a separate fresh-environment installation from TestPyPI; that particular verification should not be claimed as completed.

**Build command:**

```powershell
uv build
```

**Observed build output:**

```text
Building source distribution...
Building wheel from source distribution...
Successfully built dist\epita_group2-0.1.0.tar.gz
Successfully built dist\epita_group2-0.1.0-py3-none-any.whl
```

**Publish command:**

```powershell
uv publish --publish-url https://test.pypi.org/legacy/
```

The terminal recorded both the Wheel and source distribution being uploaded. The TestPyPI package page was also shown in the conversation. Publishing credentials are intentionally omitted.

### 2. Packaging theory

**What is a source distribution (`sdist`)?** A `.tar.gz` source distribution contains the project's source and build metadata; installing it may require a build step on the target machine.

**What is a Wheel?** A `.whl` is a built distribution in a standardized format that an installer can unpack directly for a compatible Python environment, normally without building the package from source.

**Why can Wheels be faster and safer?** They usually install faster because they avoid building on the user's machine. They can also reduce build-time code execution and variability associated with local compilation or build dependencies. However, a Wheel is not automatically trustworthy: its source and integrity still matter.

## Part 5: Professional Debugging Challenge (No `print()` for debugging)

### 1. Root cause analysis

The original `parse_api_record()` function used `.split(",")`, which produced strings. Therefore, both `record["volume"]` and `record["weight"]` were initially of type `str`.

In post-mortem debugging, We inspected:

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

Python cannot multiply two string operands. If the multiplication problem were corrected without converting `volume` to a number, the later `total_volume += record["volume"]` would also be invalid because it adds a string to an integer.

### 2. Conditional breakpoint and call stack

We placed a conditional breakpoint on line 32 in `aggregate_telemetry()`:

```text
(Pdb) b 32, idx == 2
(Pdb) c
```

After correcting the types, execution paused at:

```text
...debug_challenge.py(32)aggregate_telemetry()
-> impact = compute_weighted_metric(record["volume"], record["weight"])
```

We inspected the record and types:

```text
(Pdb) p type(record["volume"]), type(record["weight"])
(<class 'int'>, <class 'int'>)

(Pdb) p record
{'id': 'REC_003', 'entity': 'service_gamma', 'volume': 450, 'status': 'SUCCESS', 'weight': 3}
```

**Observed `where` call stack at the conditional breakpoint:**

1. Debugger execution wrapper (`bdb.py`, `run()`), followed by the execution `<string>` module frame.
2. `debug_challenge.py` top-level `<module>` frame, calling `aggregate_telemetry(api_payload)` on line 57.
3. `aggregate_telemetry()` frame, paused at line 32 immediately **before** the call to `compute_weighted_metric()`.

**Additional call stack from the original TypeError:** The earlier exception traceback included `<module>` → `aggregate_telemetry()` → `compute_weighted_metric()` (line 20). Thus, the calculation function frame was visible during the failure. At the later conditional breakpoint, we inspected `where` before stepping into that function, so `compute_weighted_metric()` was not yet on that particular stack.

### 3. The fix

We converted both numerical fields when parsing each CSV-like record:

```diff
- "volume": parts[2],
+ "volume": int(parts[2]),
  "status": parts[3],
- "weight": parts[4]
+ "weight": int(parts[4])
```

This ensures numeric multiplication and aggregation. In the sample data, all the values are integers.

### 4. Verified execution output

After correcting the script, we continued it in Pdb with `c`, and the program produced:

```text
Aggregate Result: {'successful_entries': 3, 'total_volume': 650, 'avg_volume': 216.66666666666666, 'high_impact_count': 1}
```

This is consistent with the three successful records: volumes `120 + 450 + 80 = 650`, average volume `650 / 3`, and one high-impact record (`450 × 3 = 1350`, greater than 500). The provided history verifies this output during debugging; it does not contain a separate final non-debugger execution of `uv run python scripts/debug_challenge.py`.

---

## Final verification items before submitting

- **Group/provider discrepancy:** The distributed roster says Group 2 uses CryptoCompare, whereas the instructor directly told our team to use IPInfo. Keep the instructor's clarification available if asked.
- **Command naming:** The actual configured CLI is `epita-epita-group2-cli`, which differs from the group roster's suggested `epita-group2-cli`. Confirm whether that exact naming is required.
- **Fresh installation test:** The supplied history confirms local CLI execution, but not execution after installing the published package into a clean environment.
- **Group verification command:** Its output was not found in the supplied history.
- **Separate normal-mode debug run:** The final dictionary is verified in Pdb, but a standalone execution after the fix was not documented.
- **Submission filename:** The group roster and full lab document use different conventions (`TP2_GROUP_2.zip` versus `TP2_LASTNAME_Firstname.zip`); follow the instructor's final submission instruction.
