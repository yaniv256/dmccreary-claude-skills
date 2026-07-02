# String Methods

Python strings come with a powerful built-in toolkit.  Methods like `upper()`,
`lower()`, `split()`, and `join()` let you transform, search, and rearrange text
without writing any loops of your own.

Before you can use these labs you need the Docker service running in a terminal:

```bash
bash scripts/run-python-docker.sh
```

Leave that terminal open, then click **Run** in any lab below.

---

## Lab 1 — Changing Case

`upper()` converts every letter to uppercase; `lower()` converts every letter to
lowercase.  Neither method changes the original string — they return a **new**
string with the transformation applied.

<div id="docker-lab-1">
<div id="docker-editor-1">
<textarea id="docker-code-1" spellcheck="false">greeting = "Hello, World!"

print(greeting.upper())
print(greeting.lower())
print(greeting)          # original is unchanged
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
- Add a line that prints the greeting with `title()` — what does that method do?
- What happens when you call `.upper()` on a string that already has all capitals?

---

## Lab 2 — Splitting a String

`split()` breaks a string apart at every occurrence of a separator (a space by
default) and returns a **list** of the pieces.  This is handy for turning a
sentence into individual words, or a CSV line into fields.

<div id="docker-lab-2">
<div id="docker-editor-2">
<textarea id="docker-code-2" spellcheck="false">sentence = "the quick brown fox"
words = sentence.split()

print("Original:", sentence)
print("Words:", words)
print("Number of words:", len(words))
print("First word:", words[0])
print("Last word:", words[-1])
</textarea>
<div id="docker-buttons-2">
  <button id="docker-run-2" onclick="runDocker('2')">&#9654; Run</button>
  <button id="docker-reset-2" onclick="resetDocker('2')">&#8635; Reset</button>
</div>
<pre id="docker-output-2" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Replace the sentence with `"red,green,blue"` and change `split()` to
  `split(",")` — what does the list look like now?
- Try `"one::two::three".split("::")` — what separator did you use?
- What does `"hello".split("l")` produce?  Predict first, then run.

---

## Lab 3 — Joining a List into a String

`join()` is the reverse of `split()`.  You call it on the **separator** string
and pass the list of pieces you want glued together.

<div id="docker-lab-3">
<div id="docker-editor-3">
<textarea id="docker-code-3" spellcheck="false">words = ["Python", "is", "fun"]

joined_space = " ".join(words)
joined_dash  = "-".join(words)
joined_none  = "".join(words)

print(joined_space)
print(joined_dash)
print(joined_none)
</textarea>
<div id="docker-buttons-3">
  <button id="docker-run-3" onclick="runDocker('3')">&#9654; Run</button>
  <button id="docker-reset-3" onclick="resetDocker('3')">&#8635; Reset</button>
</div>
<pre id="docker-output-3" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Change the separator to `" | "` and run again to see a pipe-separated result.
- Add `"!"` to the `words` list and run — where does it appear in each output?
- Try joining a list of single characters: `["P","y","t","h","o","n"]` with
  `""` as the separator.  What do you get?

---

## Lab 4 — Combining Methods

Methods can be chained: the output of one becomes the input of the next.  This
lab shows a realistic pattern — normalize a user's input before processing it.

<div id="docker-lab-4">
<div id="docker-editor-4">
<textarea id="docker-code-4" spellcheck="false">raw_input = "  Hello   World  From   Python  "

# Strip leading/trailing spaces, then split on any whitespace,
# then rejoin with a single space — a clean, normalized string.
words     = raw_input.strip().split()
cleaned   = " ".join(words)
shouted   = " ".join(words).upper()

print("Raw    :", repr(raw_input))
print("Cleaned:", cleaned)
print("Shouted:", shouted)
print("Word count:", len(words))
</textarea>
<div id="docker-buttons-4">
  <button id="docker-run-4" onclick="runDocker('4')">&#9654; Run</button>
  <button id="docker-reset-4" onclick="resetDocker('4')">&#8635; Reset</button>
</div>
<pre id="docker-output-4" class="docker-output">Output will appear here after you click Run.</pre>
</div>
</div>

**Try these experiments:**

- Replace `raw_input` with a CSV line like `"  alice , bob , carol  "` and split
  on `","` — then strip each element with a list comprehension:
  `[w.strip() for w in words]`.
- Chain `.lower()` instead of `.upper()` and see how the output changes.
- Try `raw_input.split()` without calling `.strip()` first — does the word count
  change?  Why or why not?
