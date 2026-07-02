# Functions in Docker

Run bash scripts/run-python-docker.sh in a terminal first.

## Lab 1 — Defining a Function

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" spellcheck="false">def greet(name):
    print("Hello,", name)

greet("Alice")
greet("Bob")
</textarea>
<div id="docker-buttons-1">
  <button id="docker-run-1" onclick="runDocker('1')">&#9654; Run</button>
  <button id="docker-reset-1" onclick="resetDocker('1')">&#8635; Reset</button>
</div>
<pre id="docker-output-1" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

## Lab 2 — Recursive Function: Factorial

A **recursive function** is one that calls itself. This example computes the factorial of a
number: `factorial(5)` returns `5 × 4 × 3 × 2 × 1 = 120`.

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" spellcheck="false">def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

for i in range(6):
    print(f"{i}! = {factorial(i)}")
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

## Lab 3 — Function with Default Arguments

Python lets you give a function parameter a **default value**. If the caller does not pass
that argument, the default is used automatically.

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" spellcheck="false">def power(base, exponent=2):
    return base ** exponent

print(power(3))        # uses default exponent of 2  → 9
print(power(3, 3))     # overrides default            → 27
print(power(2, 10))    # 2 to the power of 10        → 1024
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>
