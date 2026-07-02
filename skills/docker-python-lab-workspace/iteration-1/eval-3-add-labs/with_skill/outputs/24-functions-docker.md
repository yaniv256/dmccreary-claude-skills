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

---

## Lab 2 — Recursive Function: Factorial

A **recursive function** is one that calls itself. The factorial of a number `n`
(written `n!`) is `n × (n-1) × (n-2) × … × 1`. For example, `5! = 120`.
The function below solves this by calling itself with a smaller value each time,
stopping when it reaches the base case (`n == 0`).

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" spellcheck="false">def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print("0! =", factorial(0))
print("1! =", factorial(1))
print("5! =", factorial(5))
print("10! =", factorial(10))
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change `factorial(10)` to `factorial(12)` and run again — how big does the number get?
- What happens if you call `factorial(-1)`? (Hint: the recursion never reaches 0.)
- Add a `print` inside the function to trace each call, e.g. `print("factorial(", n, ")")`.

---

## Lab 3 — Default Arguments

Python lets you give a function parameter a **default value**. If the caller
does not pass that argument, the default is used automatically. This makes
functions more flexible without requiring extra code at every call site.

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" spellcheck="false">def greet(name, greeting="Hello"):
    print(greeting + ", " + name + "!")

greet("Alice")
greet("Bob", "Hi")
greet("Carol", "Good morning")
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change the default greeting from `"Hello"` to `"Hey"` and run again.
- Add a second default parameter, e.g. `punctuation="!"`, and use it in the print.
- Call `greet("Dave")` without a second argument — which greeting does it use?
