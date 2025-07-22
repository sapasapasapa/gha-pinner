# 📌 gha-pinner

## Table of Contents

- [🤔 Why should you pin your GitHub Actions?](#-why-should-you-pin-your-github-actions)
- [🚀 What does `gha-pinner` do?](#-what-does-gha-pinner-do)
- [📦 Installation](#-installation)
- [🛠️ Usage](#️-usage)

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

It can also update all actions in a workflow file in place.

## 📦 Installation

You can install `gha-pinner` using pip:

```bash
pip install gha-pinner
```

## 🛠️ Usage

Ready to lock down your workflows? Here's how you can use `gha-pinner`.

**Pin a single action:**

To get the commit SHA for a specific action, you can use the `-a` or `--action` flag:

```bash
$ gha-pinner --action actions/checkout@v3
Original: actions/checkout@v3
Pinned:   actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b
```

You can then use the pinned version in your GitHub Actions workflow file:

```yaml
- uses: actions/checkout@44c2b7a8a4ea60a981eaca3cf939b5f4305c123b
```

This ensures that you are always using the exact same version of the action, protecting you from any potential malicious updates.

**Pin an entire workflow file:**

To pin all actions in a workflow file, you can use the `-f` or `--file` flag:

```bash
$ gha-pinner --file .github/workflows/ci.yml
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
