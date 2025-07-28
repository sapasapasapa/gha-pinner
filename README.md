# 📌 gha-pinner

## Table of Contents

- [🤔 Why should you pin your GitHub Actions?](#-why-should-you-pin-your-github-actions)
- [🚀 What does `gha-pinner` do?](#-what-does-gha-pinner-do)
- [📦 Installation](#-installation)
- [🛠️ Usage](#️-usage)
- [🔄 Using as a GitHub Action](#-using-as-a-github-action)
- [👨‍💻 For Maintainers](#-for-maintainers)

## 🤔 Why should you pin your GitHub Actions?

Ever felt a bit of a thrill-seeker using `actions/checkout@v3` or even `actions/checkout@main` in your workflows? While convenient, using floating references like tags, branches, or the `latest` tag means you're living on the edge.

Pinning your GitHub Actions to a specific commit SHA is your seatbelt for this ride. Here's why it's a non-negotiable security best practice:

- **🔐 Rock-Solid Immutability**: A commit SHA is a unique, unchangeable fingerprint for a specific version of the code. No surprises. You can be absolutely certain about the code executing in your workflow.
- **🛡️ Dodge Malicious Updates**: Tags (like `v3`), branches (like `main`), and even the `latest` keyword are mutable pointers. The repository owner can move them to a different commit, potentially slipping malicious code into your workflow without you ever knowing. Pinning to a SHA is like saying, "I'll have *this* exact version, and nothing else, thank you."
- **✅ Crystal-Clear Verifiability**: A pinned SHA lets you put on your detective hat. You can browse the repository at that exact commit, inspect the code, and confirm it's safe and sound.

## 🚀 What does `gha-pinner` do?

`gha-pinner` is your friendly neighborhood GitHub Actions detective. It's a simple command-line tool that does the hard work of pinning your actions for you.

Given a GitHub Action in the format `owner/repo@ref` (where `ref` can be a branch, tag, or even `latest`), `gha-pinner` will:

1.  **🔎 Track Down the `ref`**: It sleuths out the provided `ref` and resolves it to a specific, full-length commit SHA.
2.  **📍 Serve the Pinned Version**: It then hands you back the action, neatly pinned to that commit SHA.

For example, if you provide `actions/checkout@v3`, `gha-pinner` will resolve `v3` to the latest commit SHA in the `v3` tag and provide you with `actions/checkout@<commit_sha>`.

It can also update all actions in a workflow file or directory in place.

## 📦 Installation

You can install `gha-pinner` using pip:

```bash
pip install gha-pinner
```

## 🛠️ Usage

Ready to lock down your workflows? Here's how you can use `gha-pinner`.

**Pin a single action:**

To get the commit SHA for a specific action, use the `action` subcommand:

```bash
$ gha-pinner action actions/checkout@v3
Original: actions/checkout@v3
Pinned:   actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b
```

You can then use the pinned version in your GitHub Actions workflow file:

```yaml
- uses: actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b
```

This ensures that you are always using the exact same version of the action, protecting you from any potential malicious updates.

**Pin an entire workflow file:**

To pin all actions in a workflow file, use the `file` subcommand:

```bash
$ gha-pinner file .github/workflows/ci.yml
✅ Successfully pinned actions in '.github/workflows/ci.yml'
```

This will update the file in place, pinning all actions to their latest commit SHA and adding a comment with the original version, so you don't forget where you came from. For example:

```yaml
- uses: actions/checkout@v3
```

will be updated to:

```yaml
- uses: actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b # v3
```

**Pin all workflow files in a directory:**

To pin all actions in all workflow files within a directory (recursively), use the `dir` subcommand:

```bash
$ gha-pinner dir .github/workflows
✅ Successfully pinned actions in '.github/workflows/ci.yml'
✅ Successfully pinned actions in '.github/workflows/release.yml'
```

This will scan the specified directory recursively, finding all workflow files (`.yml` and `.yaml` files), and pin all actions in each file. It's a convenient way to secure all your workflows at once.

**Validate actions without modifying files:**

To check if all actions in your workflows are properly pinned without modifying any files, use the `--validate` flag:

```bash
$ gha-pinner dir .github/workflows --validate
❌ - actions/checkout@v3 should be pinned as actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b
✅ Successfully validated actions in '.github/workflows/ci.yml'
```

When using the `--validate` flag, the command will exit with a non-zero status code if any actions need pinning, making it perfect for CI/CD pipelines.

## 🔄 Using as a GitHub Action

You can use `gha-pinner` as a GitHub Action in your workflows to validate that your actions are properly pinned.

### Validate Actions in CI/CD

Add this to your workflow to validate that all actions are properly pinned:

```yaml
name: Validate Actions

on:
  pull_request:
    paths:
      - '.github/workflows/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate GitHub Actions
        uses: gha-pinner/gha-pinner@v1
        with:
          target: '.github/workflows'
          target-type: 'dir'
```

This will fail the workflow if any actions are not properly pinned, ensuring your team follows security best practices.

## 👨‍💻 For Maintainers

### Release Process

This project uses a dual release mechanism to publish both a PyPI package and a GitHub Action:

1. **Creating a Release**:
   - To create a new release, push a tag in the format `v{major}.{minor}.{patch}` (e.g., `v1.2.3`)
   - This will trigger the release workflow

2. **What Happens During Release**:
   - Tests and linting are run
   - The package is built and published to PyPI
   - A GitHub Release is created with the version tag (e.g., `v1.2.3`)
   - A major version tag (e.g., `v1`) is automatically created/updated to point to the latest release

3. **Version References**:
   - For PyPI and specific version references, use the full version tag (e.g., `v1.2.3`)
   - For GitHub Action references in workflows, use the major version tag (e.g., `v1`)

Example:
```yaml
- name: Pin GitHub Actions
  uses: sapasapasapa/gha-pinner@v1  # This will always use the latest v1.x.x release
```

This approach ensures that users of the GitHub Action automatically get the latest patch and minor updates while maintaining compatibility, while also allowing specific version pinning for those who need it.
