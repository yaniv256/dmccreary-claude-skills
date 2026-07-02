# List Operations in Docker

Lists are one of Python's most powerful and versatile data structures.
They let you store many values under a single variable name and work
with collections of data — a shopping list, a roster of students, a
sequence of scores.

In these labs you will run real Python (not browser-emulated Python)
inside an isolated Docker container, so you get the full Python standard
library and accurate timing.

---

## Before You Begin — Start the Docker Service

You must have the Docker execution service running in a separate terminal
before the labs on this page will work.

**Open a terminal in the project folder and run:**

```sh
bash scripts/run-python-docker.sh
```

Once the service is running you will see:

```
Python Docker execution service
Listening on:  http://127.0.0.1:5001
```

Leave that terminal open while you work through this page.

---

## Lab 1 — Creating and Printing a List

A Python list is created with square brackets.  You can store any mix
of values — strings, numbers, or even other lists — and print the whole
thing at once or loop through it item by item.

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" spellcheck="false">fruits = ["apple", "banana", "cherry", "date", "elderberry"]

print("My fruit list:", fruits)
print("Number of fruits:", len(fruits))
print()

print("Printing one at a time:")
for fruit in fruits:
    print(" -", fruit)
</textarea>
<div id="docker-buttons-1">
  <button id="docker-run-1" onclick="runDocker('1')">&#9654; Run</button>
  <button id="docker-reset-1" onclick="resetDocker('1')">&#8635; Reset</button>
</div>
<pre id="docker-output-1" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Add two more fruits to the list and run again — does `len()` update automatically?
- Access a single item by its index: add `print(fruits[0])` to print the first fruit.
- Try a negative index: `print(fruits[-1])` — what does that give you?
- Replace the fruit list with a list of numbers: `scores = [95, 87, 72, 100, 65]`
  and print their sum with `print(sum(scores))`.

---

## Lab 2 — Append and Remove

Lists are *mutable* — you can change them after they are created.
The two most common ways to change a list are `append()` (to add an item
at the end) and `remove()` (to delete the first matching item by value).

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" spellcheck="false">shopping = ["milk", "eggs", "bread"]
print("Starting list:", shopping)

# Add items with append()
shopping.append("butter")
shopping.append("cheese")
print("After two appends:", shopping)

# Remove an item by value
shopping.remove("eggs")
print("After removing 'eggs':", shopping)

# Insert at a specific position
shopping.insert(1, "yogurt")
print("After inserting 'yogurt' at index 1:", shopping)

print()
print("Final list has", len(shopping), "items.")
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Use `shopping.pop()` (no argument) to remove the *last* item — print the list before and after.
- Use `shopping.pop(0)` to remove the *first* item.
- Try `shopping.sort()` then print — what order does sorting produce for strings?
- Try to `remove()` an item that is not in the list, like `shopping.remove("pizza")` — what error do you get?

---

## Lab 3 — List Comprehensions

A *list comprehension* is a compact, readable way to build a new list
from an existing one.  Instead of writing a `for` loop and calling
`append()` every time, you describe the transformation in a single line
inside square brackets.

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" spellcheck="false">numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Square every number
squares = [n ** 2 for n in numbers]
print("Squares:", squares)

# Keep only the even numbers
evens = [n for n in numbers if n % 2 == 0]
print("Even numbers:", evens)

# Convert a list of words to uppercase
words = ["python", "list", "comprehension", "rocks"]
upper_words = [w.upper() for w in words]
print("Uppercase:", upper_words)

# Combine filter + transform: square only the odd numbers
odd_squares = [n ** 2 for n in numbers if n % 2 != 0]
print("Squares of odd numbers:", odd_squares)
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Build a list of the first 10 multiples of 3: `[n * 3 for n in range(1, 11)]`.
- Create a list of string lengths: `[len(w) for w in words]`.
- Filter the `squares` list to keep only values greater than 25.
- Rewrite the `evens` comprehension as a traditional `for` loop with `append()` —
  both approaches produce the same result.

---

## Key Concepts Recap

| Operation | Syntax | What it does |
|-----------|--------|--------------|
| Create a list | `my_list = [1, 2, 3]` | Makes a new list with initial values |
| Access by index | `my_list[0]` | Gets the item at position 0 (first item) |
| Get length | `len(my_list)` | Returns the number of items |
| Add to end | `my_list.append(x)` | Adds `x` as the last item |
| Remove by value | `my_list.remove(x)` | Removes the first occurrence of `x` |
| Remove by position | `my_list.pop(i)` | Removes and returns the item at index `i` |
| Insert at position | `my_list.insert(i, x)` | Inserts `x` before index `i` |
| Sort in place | `my_list.sort()` | Sorts the list (smallest to largest) |
| List comprehension | `[expr for item in iterable if cond]` | Builds a new list from an existing one |

---

## Troubleshooting

**"Cannot connect to the Python Docker service"**
: The service is not running.  Open a terminal and run `bash scripts/run-python-docker.sh`.

**"IndexError: list index out of range"**
: You tried to access an index that does not exist.  Remember: a list with 5 items has
  indices 0 through 4 — index 5 is out of range.

**"ValueError: list.remove(x): x not in list"**
: You tried to `remove()` a value that was not found.  Check your spelling or use
  `if x in my_list:` before calling `remove()`.
