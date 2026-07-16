# Docker Python Lab Guide

> Formerly the standalone skill `docker-python-lab`.

## What This Guide Does

Generates the client-only browser interface for interactive Python lab blocks in
MkDocs pages. Each lab shows a code editor, Run and Reset buttons, and an output
area. A separately reviewed local service must run the code in a fresh Docker
container; this skill does not provide that execution service.

This is the Docker counterpart to the Skulpt lab pattern: students run real
Python rather than browser-emulated Python. The default image provides the Python
standard library only. Extra packages are available only when the target project
explicitly builds and reviews an image that installs them.

Use it whenever someone asks to add a Python lab, code runner, interactive Python
exercise, or runnable code block to a textbook page that uses Docker (not Skulpt).
Always follow this guide instead of writing docker lab HTML by hand.

---

## Prerequisites: Shared Infrastructure

Before generating any lab block, verify the execution boundary first. Check once
per session; skip file installation only after the service passes this gate.

### 1. Verify a reviewed execution service exists

The browser assets in this skill send learner-authored Python to
`http://127.0.0.1:5001/run`. They do not implement that endpoint. The target
project must provide `scripts/run-python-docker.sh` and the server it launches.

**STOP: do not generate or install a Docker Python lab** when the script or its
server implementation is missing. Do not copy the client assets, modify
`mkdocs.yml`, or add lab markup that would look complete but cannot run.

Before proceeding, inspect the implementation and verify all of these controls:

- The HTTP server binds to `127.0.0.1 only`, not `0.0.0.0`, by default.
- CORS and server-side origin checks use an explicit allowlist of browser
  origins; wildcard, missing, and `null` origins are rejected. `POST /run`
  accepts only `Content-Type: application/json` after a successful preflight.
- Every run uses a fresh container with `--rm`, `--network none`, `--read-only`,
  `--cap-drop=ALL`, `--security-opt no-new-privileges`, and a non-root user.
- The command rejects `--privileged`, device access, host PID/IPC/user namespace
  sharing, added Linux capabilities, and unconfined seccomp or AppArmor. Keep
  Docker's default seccomp and host LSM policy or use a stricter reviewed policy.
- The image is pinned by digest. Docker arguments are a fixed argv array; learner
  code is passed over standard input and is never interpolated into a host shell
  command, Docker argument, filename, or environment variable.
- Before generation, the project records reviewed numeric ceilings for
  `--memory`, `--cpus`, `--pids-limit`, request bytes, streamed output bytes,
  execution time, queued requests, and concurrent containers. A full queue fails
  fast rather than growing without bound.
- The container receives no host filesystem mounts, Docker socket, or inherited
  secrets, and only a size-limited temporary filesystem when one is required.
- The server enforces request limits before Docker starts and enforces output
  limits while streaming. On timeout, output cap, client disconnect, server
  shutdown, or internal error, it forcibly stops and removes the container before
  releasing the request slot; `--rm` alone is not a cleanup strategy.
- The server accepts `POST /run` JSON containing only `code` and optional
  `show_timing`, rejecting unknown fields. It returns bounded JSON with `stdout`,
  `stderr`, and `returncode`. When timing is requested, it reports directly
  measured `docker_total_ms`, `server_overhead_ms`, `container_startup_ms`, and
  `python_exec_ms`. `server_overhead_ms` excludes `docker_total_ms`;
  `docker_total_ms` includes startup, execution, and any other container overhead.
- An acceptance check proves disallowed origins fail, outbound network access
  fails, filesystem changes do not persist, runaway code times out, oversized
  input/output is rejected or truncated while streaming, overload fails fast,
  forbidden Docker options cannot be introduced, and the container is removed
  after every success, timeout, disconnect, output cap, and server shutdown.

This checklist is a review boundary, not a server implementation. A public or
remote execution service needs a separate threat model and is outside this guide.

### 2. Check / create `docs/css/docker-lab.css`

If the file is missing, copy from this skill's assets:

```bash
cp ~/.claude/skills/microsim-generator/assets/docker-python-lab/docker-lab.css \
   docs/css/docker-lab.css
```

### 3. Check / create `docs/js/docker-lab.js`

```bash
cp ~/.claude/skills/microsim-generator/assets/docker-python-lab/docker-lab.js \
   docs/js/docker-lab.js
```

### 4. Add to `mkdocs.yml` (if not already present)

Check `extra_css` and `extra_javascript` in `mkdocs.yml`.  If the entries are
missing, add them:

```yaml
extra_css:
  - css/docker-lab.css      # ← add this line

extra_javascript:
  - js/docker-lab.js        # ← add this line
```

Do **not** duplicate entries that are already there.

---

## Lab HTML Template

Each lab needs a unique **suffix** — a short string that distinguishes it from
other labs on the same page.  Use `"1"` for the first lab, `"2"` for the second,
and so on.  The suffix appears in every element ID so the JS can find the right
elements.

### Standard lab (text output only)

```html
<div id="docker-lab-SUFFIX">
<div id="docker-editor-SUFFIX">
<textarea id="docker-code-SUFFIX" spellcheck="false">PYTHON_CODE_HERE
</textarea>
<div id="docker-buttons-SUFFIX">
  <button id="docker-run-SUFFIX" onclick="runDocker('SUFFIX')">&#9654; Run</button>
  <button id="docker-reset-SUFFIX" onclick="resetDocker('SUFFIX')">&#8635; Reset</button>
</div>
<pre id="docker-output-SUFFIX" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>
```

**Rules:**

- Replace every `SUFFIX` with the same string (e.g., `1`, `2`, `hello-world`).
- Put the Python code directly inside the `<textarea>` tag — no extra indentation
  relative to column 0, because leading spaces become part of the code.
- The `</textarea>` closing tag must be on its own line with no trailing spaces
  before it; any blank line between the code and `</textarea>` adds an empty line
  in the editor.
- Do **not** add `rows="N"` — the JS auto-sizes the textarea to fit the code.
- Do **not** add `id="main"` to any element — that conflicts with the p5.js canvas
  parent convention used elsewhere in this project.

### Timed lab (shows measured timing breakdown)

Only add this variant when the lesson is specifically about how Docker execution
works and the reviewed service returns documented timing fields. It requires
suffix `"4"` by convention. The browser measures total round-trip time. It may
derive only the combined browser and network overhead; it cannot infer separate
outbound and return network times.

```html
<div id="docker-lab-4">
<div id="docker-editor-4">
<textarea id="docker-code-4" spellcheck="false">PYTHON_CODE_HERE
</textarea>
<div id="docker-buttons-4">
  <button id="docker-run-4" onclick="runDockerTimed()">&#9654; Run + Time</button>
  <button id="docker-reset-4" onclick="resetDockerTimed()">&#8635; Reset</button>
</div>
</div>
<div id="docker-timing-display" style="display:none; margin-top:12px;">
  <table id="docker-timing-table">
    <thead>
      <tr><th>#</th><th>Phase</th><th style="text-align:right">Time (ms)</th><th>Bar</th></tr>
    </thead>
    <tbody>
      <tr><td>1</td><td>Browser and network overhead (combined)</td>
          <td id="td-roundtrip-overhead" style="text-align:right">—</td>
          <td><div class="timing-bar" id="bar-roundtrip-overhead"></div></td></tr>
      <tr><td>2</td><td>Server overhead</td>
          <td id="td-server-overhead" style="text-align:right">—</td>
          <td><div class="timing-bar" id="bar-server-overhead"></div></td></tr>
      <tr><td>3</td><td>Container startup</td>
          <td id="td-startup" style="text-align:right">—</td>
          <td><div class="timing-bar" id="bar-startup"></div></td></tr>
      <tr><td>4</td><td>Python execution</td>
          <td id="td-exec" style="text-align:right">—</td>
          <td><div class="timing-bar" id="bar-exec"></div></td></tr>
      <tr><td>5</td><td>Other container overhead</td>
          <td id="td-container-overhead" style="text-align:right">—</td>
          <td><div class="timing-bar" id="bar-container-overhead"></div></td></tr>
      <tr style="font-weight:bold; border-top: 2px solid #642580;">
          <td colspan="2">Total round-trip</td>
          <td id="td-total" style="text-align:right">—</td>
          <td></td></tr>
    </tbody>
  </table>
  <p id="docker-timing-note" style="font-size:0.85em; color:#666; margin-top:6px;"></p>
</div>
<pre id="docker-output-4" class="docker-output" style="margin-top:10px;">Output will appear here after you click Run + Time.</pre>
</div>
```

---

## Complete Page Pattern

A page with three labs looks like this:

```markdown
# Page Title

Intro text explaining what the page covers and that students must run
`bash scripts/run-python-docker.sh` in a separate terminal first.

## Lab 1 — Hello, World!

Brief explanation of what this lab demonstrates.

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" spellcheck="false">print("Hello, World!")
</textarea>
<div id="docker-buttons-1">
  <button id="docker-run-1" onclick="runDocker('1')">&#9654; Run</button>
  <button id="docker-reset-1" onclick="resetDocker('1')">&#8635; Reset</button>
</div>
<pre id="docker-output-1" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**
- Change the message and run again.

---

## Lab 2 — Variables

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" spellcheck="false">x = 42
print("The answer is", x)
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>
```

---

## Choosing Good Lab Code

- **Keep starter code short** (5–15 lines) so students can read it at a glance.
- **Every lab should produce visible output** — at least one `print()` call.
- **Avoid `input()`** — there is no stdin in the Docker runner.
- **Avoid file I/O** — the container has no persistent filesystem.
- **Avoid `import` of non-stdlib packages** unless the reviewed target image
  explicitly installs them. `python:3.11-alpine` supplies the stdlib, not an
  open-ended package environment.
- Match the "See It — Run It — Modify It" rhythm from the Skulpt labs:
  starter code runs and shows something, then "Try these experiments" gives
  specific, achievable modifications.

---

## Service Not Running — User-Facing Error

If a student clicks Run before starting the service, the lab shows:

> Cannot connect to the Python Docker service.
> Please open a terminal and run:
>   bash scripts/run-python-docker.sh
> Then reload this page and try again.

No extra error handling is needed in the page markdown — `docker-lab.js` handles
this automatically.

---

## Multiple Labs per Page — Checklist

When generating labs for a single page:

- [ ] The reviewed execution service and every sandbox control above are present
- [ ] Each lab has a **unique suffix** — `1`, `2`, `3`, …
- [ ] Every element ID includes that suffix (`docker-lab-1`, `docker-code-1`, etc.)
- [ ] Button `onclick` passes the matching suffix string: `runDocker('2')`
- [ ] No two labs share a suffix on the same page
- [ ] The page opens with a "Start the Docker service" instruction block
- [ ] `docs/css/docker-lab.css` and `docs/js/docker-lab.js` are in `mkdocs.yml`
