# Auto-Commenting Java Code with GitHub Actions

This guide explains how to set up **auto-commenting** for Java files using `auto_comment.py` with **GitHub Actions**. The github action will detect only the modified Java files and add comments to it.

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- `git` installed and configured
- A GitHub repository
- A valid AI API key (if required for AI-generated comments)
- You can get an AI model API KEY from here - `https://github.com/marketplace/models`

## Setup Instructions

### 1️⃣ Clone the Repository

```sh
 git clone <your-repo-url>
 cd <your-repo>
```

### 2️⃣ Ensure `.github/workflows/auto_comment.yml` Exists

After cloning the repository, the `.github/workflows/auto_comment.yml` file should already be present. If it does not exist, create it manually using:

```sh
mkdir -p .github/workflows
nano .github/workflows/auto_comment.yml
```

Add the following YAML configuration:

```yaml
name: Auto-Comment Java Code

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  auto_comment:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 2  # Ensure previous commit is available for comparison

      - name: Set Up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install Dependencies
        run: pip install -r requirements.txt


      - name: Load Environment Variables
        run: echo "GITHUB_TOKEN=${{ secrets.AUTO_COMMENT_TOKEN }}" > .env

      - name: Find Modified Java Files
        id: changed_files
        run: |
          if git rev-parse HEAD~1 >/dev/null 2>&1; then
            PREV_COMMIT=$(git rev-parse HEAD~1)
          else
            PREV_COMMIT=$(git rev-list --max-parents=0 HEAD)  # First commit in repo
          fi
          LAST_COMMIT=$(git rev-parse HEAD)
          
          # Get list of changed Java files
          CHANGED_FILES=$(git diff --name-only $PREV_COMMIT $LAST_COMMIT -- '*.java')
          
          if [[ -z "$CHANGED_FILES" ]]; then
            echo "No Java files changed."
            echo "changed_files=" >> $GITHUB_ENV
          else
            echo "Modified Java files: $CHANGED_FILES"
            echo "changed_files=$CHANGED_FILES" >> $GITHUB_ENV
          fi

      - name: Run Auto Comment Script
        run: |
          if [[ -n "${{ env.changed_files }}" ]]; then
            for file in ${{ env.changed_files }}; do
              python auto_comment.py "$file"
            done
          else
            echo "No Java files to process."
          fi

      - name: Commit Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          git commit -m "Auto-commented Java files" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.AUTO_COMMENT_TOKEN }}
```

### 3️⃣ Add `auto_comment.py` to Your Repository

Ensure `auto_comment.py` is in your repository root. This script should:

- Detect modified Java files
- Add AI-generated comments
- Overwrite the files with updated comments

### 4️⃣ Add `.env` file to your repository and add secret variable in settings

- create a variable with name `GITHUB_TOKEN` and assign your API KEY as value.
- go to `Settings -> Secrets and variables -> Actions` and create a secret variable with name `AUTO_COMMENT_TOKEN` and provide API KEY as value

### 5️⃣ Commit and Push

```sh
git add .
git commit -m "Add auto-comment workflow"
git push origin main
```
- The workflow will run automatically on push and pull, adding comments to modified Java files.
- Ensure that the necessary API key is added as a **GitHub Actions secret** under `Settings -> Secrets and variables -> Actions`.

## Final Points

make sure your Java project contains following files:
- .github/workflows/auto_comment.yml
- requirements.txt
- auto_comment.py
- .env with token

## Troubleshooting

- Check workflow logs under **GitHub Actions** → **Auto-Comment Java Code**.
- Ensure your API key (if required) is correctly configured.
- Run `python auto_comment.py` locally to verify it works.

---



