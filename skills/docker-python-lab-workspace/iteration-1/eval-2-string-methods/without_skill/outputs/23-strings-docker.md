# String Methods

Strings are one of the most useful data types in Python.  A *string* is any
sequence of characters — letters, digits, spaces, punctuation.  Python gives
you dozens of built-in methods to transform, search, and rearrange strings.

In this lab you will explore four of the most commonly used string methods:

| Method | What it does |
|--------|-------------|
| `upper()` | Returns a copy of the string in ALL CAPS |
| `lower()` | Returns a copy of the string in all lowercase |
| `split()` | Breaks a string into a list of smaller strings |
| `join()` | Glues a list of strings back together into one |

---

## Before You Begin — Start the Docker Service

You must have the Docker execution service running in a separate terminal before
the labs on this page will work.

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

## Lab 1 — `upper()` and `lower()`

`upper()` converts every letter to uppercase.  `lower()` converts every letter
to lowercase.  Neither method changes the original string — it returns a *new*
string with the change applied.

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" rows="10" spellcheck="false">greeting = "Hello, World!"

loud = greeting.upper()
quiet = greeting.lower()

print("Original:", greeting)
print("Upper:   ", loud)
print("Lower:   ", quiet)
</textarea>
<div id="docker-buttons-1">
  <button id="docker-run-1" onclick="runDocker('1')">&#9654; Run</button>
  <button id="docker-reset-1" onclick="resetDocker('1')">&#8635; Reset</button>
</div>
<pre id="docker-output-1" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change `"Hello, World!"` to your own name and run it again.
- What happens if you call `.upper()` on a string that is already uppercase?
- Try `print(greeting.upper().lower())` — can you chain two methods in a row?
- What does `.upper()` do to digits and punctuation like `"abc 123!"`?

---

## Lab 2 — `split()`

`split()` breaks a string into a **list** of smaller strings every time it sees
a separator character.  By default the separator is any whitespace (spaces,
tabs, newlines).

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" rows="14" spellcheck="false">sentence = "Python is a fun programming language"

# Split on whitespace (the default)
words = sentence.split()
print("Words:", words)
print("Number of words:", len(words))

# Split on a specific character
csv_line = "Alice,85,Python,True"
fields = csv_line.split(",")
print("\nCSV fields:", fields)
print("Student name:", fields[0])
print("Score:", fields[1])
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change `sentence` to a sentence of your own and count the words.
- Try splitting `"one:two:three:four"` using `":"` as the separator.
- What does `split()` return when there is only one word and no spaces?
- Try `"a,,b,,c".split(",")` — what happens to the empty gaps?

---

## Lab 3 — `join()`

`join()` is the *reverse* of `split()`.  It takes a list of strings and glues
them together into one string, placing a separator between each item.

Notice the syntax — the separator string comes first, then `.join(list)`:

```python
separator.join(list_of_strings)
```

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" rows="14" spellcheck="false">words = ["Python", "is", "a", "fun", "language"]

# Join with a space between words
sentence = " ".join(words)
print("Joined sentence:", sentence)

# Join with a different separator
dashes = "-".join(words)
print("Dashes:", dashes)

# Join with no separator (stick everything together)
together = "".join(words)
print("No spaces:", together)
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change the separator to `" | "` (space-pipe-space) to make a menu-style list.
- Try joining a list of your three favourite foods.
- What happens if you join a list that has only one item?
- Join with `"\n"` (a newline) — does each word appear on its own line?

---

## Lab 4 — Putting It All Together

`split()` and `join()` work beautifully as a pair.  A common pattern is:

1. Split a sentence into words.
2. Transform each word (upper, lower, or anything else).
3. Join the words back into a sentence.

<div id="docker-lab-4">
<div id="docker-editor-4">
<textarea id="docker-code-4" rows="18" spellcheck="false">original = "the quick brown fox jumps over the lazy dog"

# Step 1 — split into a list of words
words = original.split()

# Step 2 — capitalise each word
titled = []
for word in words:
    titled.append(word[0].upper() + word[1:])

# Step 3 — join back into a sentence
result = " ".join(titled)

print("Original:", original)
print("Title case:", result)
print("SHOUTING:", original.upper())
print("whisper:", original.lower())
</textarea>
<div id="docker-buttons-4">
  <button id="docker-run-4" onclick="runDocker('4')">&#9654; Run</button>
  <button id="docker-reset-4" onclick="resetDocker('4')">&#8635; Reset</button>
</div>
<pre id="docker-output-4" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change `original` to the title of your favourite book or movie.
- Python actually has a built-in `.title()` method.  Try `original.title()` — does it match what the loop does?
- Modify the loop to make every *other* word uppercase.
- Count how many times the word `"the"` appears: `words.count("the")`.

---

## Quick Reference

Here is a summary of what you practised today.

```python
s = "Hello, World!"

# Case conversion
s.upper()           # "HELLO, WORLD!"
s.lower()           # "hello, world!"

# Split a string into a list
s.split()           # ['Hello,', 'World!']
s.split(",")        # ['Hello', ' World!']

# Join a list into a string
words = ["Hello", "World"]
" ".join(words)     # "Hello World"
", ".join(words)    # "Hello, World"
```

---

## Troubleshooting

**"Cannot connect to the Python Docker service"**
: The service is not running.  Open a terminal and run `bash scripts/run-python-docker.sh`.

**"Docker error: ..."**
: Make sure Docker Desktop is running (look for the whale icon in your menu bar or system tray).

**"Timed out after 10 seconds"**
: Your program ran too long.  Check for an infinite loop (`while True:` with no `break`).
