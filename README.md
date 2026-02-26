# Quick Prompter

Quick Prompter fills in prompt templates for you via a simple CLI. Just run the tool, answer a few questions, and your completed prompt is copied to your clipboard.

---

## What Are Placeholders?

**Placeholders** are marked sections in your prompt file that get filled in with your answers. They're wrapped in square brackets like this:

```
[Your name?]
```

When you run Quick Prompter, it finds each placeholder and asks you to provide an answer. Your answer replaces the placeholder in the final output.

---

## Types of Placeholders

### 1. Question Placeholders

Use these when you want to ask for text input. Just write your question inside square brackets.

**Format:**

```
[Your question here?]
```

**Example:**

```
[What is your project name?]
```

When you run the tool, it will ask:

```
What is your project name?
```

**Directory Questions**

If your question mentions "where", "directory", or "folder", Quick Prompter will show you a tree of folders to help you pick the right path:

**Example:**

```
[Where is your planning directory?]
```

This shows your folder structure and helps you enter the correct path.

---

### 2. Selection Placeholders

Use these when you want to offer multiple choices. The user simply picks one.

**Format:**

```
[Choice 1 OR Choice 2]
```

or

```
[Choice 1 / Choice 2]
```

**Example:**

```
[at the start of the project OR in the middle of the project]
```

When you run the tool, it will show:

```
Select:
  1. at the start of the project
  2. in the middle of the project

Enter number (default: at the start of the project)
```

The user can type `1` or `2` (or press Enter to accept the default).

---

## How to Use

### 1. Create a Prompt File

Create a `.md` file with your prompt template. Add placeholders where you want to fill in information.

**Example file: `my-prompt.md`**

```
The goal of this project is to [What do you want to build?].

We are [at the beginning OR in the middle] of development.

The planning folder is located at [Where is your planning directory?].
```

### 2. Run Quick Prompter

```bash
python quick_prompter.py my-prompt.md
```

### 3. Answer the Questions

Quick Prompter will ask you each question in order. Your answers are inserted into the placeholders.

### 4. Get Your Result

When finished, the completed prompt is **automatically copied to your clipboard**. You can paste it wherever you need it.

---

## Example Prompt File

Here's a more complete example:

```
# Project Setup Prompt

The goal of this project is to [What do you want to build? What problem does it solve?].

We are [just starting / making progress / nearly done] and need to [What do you need help with?].

You should use [Python / JavaScript / TypeScript / Rust] for this project.

The project is located at [Where is your project folder?].

Please create a detailed plan considering [Any specific requirements or constraints?].
```

When you run Quick Prompter on this file, you'll get prompted for each placeholder in order, and the final result will be a fully filled-in prompt ready to use.

---

## Quick Reference

| What You Want       | Format                    | Example                    |
| ------------------- | ------------------------- | -------------------------- |
| Ask a question      | `[Your question?]`        | `[What is your name?]`     |
| Offer choices       | `[Choice 1 OR Choice 2]`  | `[Start OR Continue]`      |
| Offer choices (alt) | `[Choice 1 / Choice 2]`   | `[Yes / No]`               |
| Ask for folder      | `[Where is your folder?]` | `[Where is your project?]` |

---

## Tips

- **Order matters**: Placeholders are filled in from top to bottom
- **Default selections**: For choices, the first option is the default (press Enter to accept)
- **Directory hints**: When asking about folders, the tool will suggest paths containing `.planning` as defaults
- **Optional answers**: If you leave a question blank, the placeholder stays in the final output
