# 📌 gha-pinner

## 🤔 Why should you pin your GitHub Actions?

Pinning your GitHub Actions to a specific commit SHA is a critical security best practice. Here's why:

- **🔐 Immutability**: Unlike tags, a commit SHA is a unique, immutable identifier for a specific version of the code. This means you can be certain about the exact code that is being executed in your workflow.
- **🛡️ Protection Against Malicious Updates**: Tags are mutable and can be updated by the repository owner to point to a different commit. This could potentially introduce malicious code into your workflow without your knowledge.
- **✅ Verifiability**: Pinning to a SHA allows you to verify the code you are using. You can browse the repository at the specific commit and ensure that it is safe to use.

## 🚀 What does `gha-pinner` do?

`gha-pinner` is a simple command-line tool that helps you pin your GitHub Actions to a specific commit SHA.

Given a GitHub Action in the format `owner/repo@ref` (where `ref` can be a branch, tag, or even `latest`), `gha-pinner` will:

1.  **🔎 Resolve the `ref`**: It will resolve the provided `ref` to a specific commit SHA.
2.  **📍 Provide the Pinned Version**: It will then provide you with the action pinned to that specific SHA.

For example, if you provide `actions/checkout@v3`, `gha-pinner` will resolve `v3` to the latest commit SHA in the `v3` tag and provide you with `actions/checkout@<commit_sha>`.

## usage

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
