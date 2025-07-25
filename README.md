
# Context Creator

Have you ever found yourself manually copying and pasting code into a single file to feed to an AI model? Or maybe you needed to give a new collaborator a quick overview of a project, but didn't want to send them a zip file full of junk.

This tool was built to solve that exact problem.

`context-creator` is a simple, powerful command-line utility that walks through your project directory, grabs all the relevant source code, and combines it all into a single, clean text file. It's smart enough to ignore the things you don't need, using a `.contextignore` file that works just like the `.gitignore` you already know and love.

The goal is simple: less time spent on tedious prep work, more time focused on what matters.

### Key Features

*   **Zero-Config Start:** Run it in any project, and it just works.
*   **Intelligent Ignoring:** Automatically creates and uses a `.contextignore` file with sensible defaults to skip dependency folders, build artifacts, and local configs.
*   **Clear, Structured Output:** The generated file starts with a directory tree, followed by the contents of each file, clearly demarcated.
*   **Fast and Focused:** A single, lightweight utility with no dependencies, designed to do one job perfectly.

### Getting Started

#### 1. Installation

The tool is hosted on PyPI. All you need is Python installed, then run:

```bash
pip install context-creator
```

#### 2. First Run

Navigate your terminal into any of your project directories and simply run the command:

```bash
context
```

The first time you run it, you'll see this output:

```
Created default .contextignore file.
Generated context.txt.
```

Two things have happened:
1.  A `context.txt` file has been created in your project root. This is your project's complete context, ready to be used.
2.  A `.contextignore` file has also been created. This comes pre-filled with common patterns to ignore things like `node_modules`, `.git`, and Python virtual environments.

### Usage

While the default is designed to be all you need, you can easily customize its behavior.

*   **Specify a directory:**
    ```bash
    context /path/to/another/project
    ```

*   **Set a custom output file name:**
    ```bash
    context -o project_overview.md
    ```

### Customizing with `.contextignore`

The real power comes from tailoring the context to your exact needs. Open the `.contextignore` file in your project. It's just a plain text file where each line is a pattern to ignore.

For example, if you want to also ignore all markdown files, just add this line:

```
*.md
```

The tool will now skip any file with a `.md` extension during its next run.

---

This project is open-source and released under the MIT License.
