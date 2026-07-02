# List Operations in Docker

In Python, a **list** is an ordered collection that can hold multiple values at once.
Lists are one of the most-used data structures in Python — you will find them in
almost every real program you ever write.

This page lets you practice list operations by running real Python code inside a
Docker container.  Each lab uses the same local Docker service from the
[Running Python in Docker](21-docker-python.md) page.

---

## Before You Begin — Start the Docker Service

The labs below need the Docker execution service running in a separate terminal.

**Open a terminal in the project folder and run:**

```sh
bash scripts/run-python-docker.sh
```

You should see:

```
Python Docker execution service
Listening on:  http://127.0.0.1:5001
```

Leave that terminal open while you work through this page.

---

## What Is a List?

A list in Python is written with square brackets `[ ]`, with items separated by commas:

```python
fruits = ["apple", "banana", "cherry"]
```

You can put numbers, strings, or even other lists inside a list.  Python lists are
**ordered** (items stay in the order you put them in) and **mutable** (you can
change them after you create them).

| Operation | Syntax | What it does |
|-----------|--------|--------------|
| Create    | `my_list = [1, 2, 3]` | Makes a new list |
| Access    | `my_list[0]`          | Gets the first item (index 0) |
| Length    | `len(my_list)`        | Counts the items |
| Append    | `my_list.append(4)`   | Adds to the end |
| Remove    | `my_list.remove(2)`   | Removes first match |
| Slice     | `my_list[1:3]`        | Gets items at index 1 and 2 |

---

## Lab 1 — Creating and Printing a List

This lab shows how to create a list and explore its contents.

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" rows="14" spellcheck="false"># Create a list of planets
planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter"]

# Print the whole list
print("All planets:", planets)

# Print the number of items
print("Number of planets:", len(planets))

# Print individual items by index
print("First planet:", planets[0])
print("Last planet:", planets[-1])

# Print a slice (items 1 through 3)
print("Inner planets (slice):", planets[1:4])
</textarea>
<div id="docker-buttons-1">
  <button id="docker-run-1" onclick="runDocker('1')">&#9654; Run</button>
  <button id="docker-reset-1" onclick="resetDocker('1')">&#8635; Reset</button>
</div>
<pre id="docker-output-1" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Add a sixth planet (`"Saturn"`) to the list and run again.
- Change `planets[-1]` to `planets[-2]` — which planet does that give you?
- Try `planets[0:2]` — how many items does that slice include?
- Replace all the planet names with your five favourite foods and print them.

---

## Lab 2 — Append and Remove

Lists are **mutable** — you can add items with `.append()` and remove them with
`.remove()` or `.pop()`.

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" rows="20" spellcheck="false"># Start with an empty shopping list
shopping = []

# Add items one at a time with append()
shopping.append("milk")
shopping.append("eggs")
shopping.append("bread")
shopping.append("butter")
print("After adding items:", shopping)

# Remove a specific item by value
shopping.remove("eggs")
print("After removing 'eggs':", shopping)

# Pop removes and returns the last item
last_item = shopping.pop()
print("Popped item:", last_item)
print("List after pop:", shopping)

# Check if an item is still in the list
print("Is 'milk' in the list?", "milk" in shopping)
print("Is 'eggs' in the list?", "eggs" in shopping)
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- After the `pop()`, use `shopping.insert(0, "coffee")` to add `"coffee"` at the
  beginning (index 0).  What does the list look like?
- Try calling `shopping.remove("eggs")` a second time — what error do you get?
- Use `shopping.sort()` before the final `print` — does alphabetical order match
  what you expect?
- Replace the shopping list with five items of your own and remove two of them.

---

## Lab 3 — List Comprehensions

A **list comprehension** is a compact way to build a new list by applying an
expression to every item in an existing list — all in a single line.

The pattern is:

```python
new_list = [expression for item in old_list]
```

You can also add a filter:

```python
new_list = [expression for item in old_list if condition]
```

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" rows="22" spellcheck="false"># Start with a list of numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Comprehension 1: square every number
squares = [n ** 2 for n in numbers]
print("Squares:", squares)

# Comprehension 2: keep only even numbers
evens = [n for n in numbers if n % 2 == 0]
print("Even numbers:", evens)

# Comprehension 3: even squares only
even_squares = [n ** 2 for n in numbers if n % 2 == 0]
print("Squares of even numbers:", even_squares)

# Comprehension 4: work with strings
words = ["hello", "python", "lists", "are", "great"]
upper_words = [w.upper() for w in words]
print("Uppercase words:", upper_words)

# Comprehension 5: filter words longer than 4 characters
long_words = [w for w in words if len(w) > 4]
print("Words longer than 4 chars:", long_words)
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change `n ** 2` to `n ** 3` to get cubes instead of squares.
- Add a sixth comprehension that creates a list of the *lengths* of each word in
  `words` — hint: `[len(w) for w in words]`.
- Modify the even-number filter to keep only numbers greater than 5 instead.
- Replace `words` with a list of your own words and find the ones longer than
  3 characters.

---

## Key Points to Remember

| Concept | Example | Result |
|---------|---------|--------|
| Create list | `x = [10, 20, 30]` | `[10, 20, 30]` |
| Access by index | `x[0]` | `10` |
| Negative index | `x[-1]` | `30` |
| Slice | `x[0:2]` | `[10, 20]` |
| Append | `x.append(40)` | `[10, 20, 30, 40]` |
| Remove by value | `x.remove(20)` | `[10, 30, 40]` |
| Pop last | `x.pop()` | returns `40`; list becomes `[10, 30]` |
| Comprehension | `[n*2 for n in x]` | `[20, 60]` |
| Filter comprehension | `[n for n in x if n > 15]` | `[30]` |

---

## How It Works

Each time you click **Run**, your code is sent to the Docker service running on
`http://127.0.0.1:5001`.  Docker starts a fresh, isolated Python container, runs
your code, captures the output, and sends it back to your browser.  The container
is deleted immediately after your program finishes.

See the [Running Python in Docker](21-docker-python.md) page for a full
explanation of the service and troubleshooting tips.

---

## Troubleshooting

**"Cannot connect to the Python Docker service"**
: The service is not running.  Open a terminal and run `bash scripts/run-python-docker.sh`.

**"Docker error: ..."**
: Make sure Docker Desktop is running (look for the whale icon in your menu bar or system tray).

**`ValueError: list.remove(x): x not in list`**
: You tried to remove a value that is not in the list.  Check for typos or make
  sure you haven't already removed that item.

**`IndexError: list index out of range`**
: You used an index number that is too large (or too negative) for the list's
  current length.  Use `len(your_list)` to check how many items it has.

---
