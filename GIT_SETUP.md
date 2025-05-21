# Git Setup for LearnMore

This guide explains how to set up and use Git for the LearnMore project.

## Initial Setup

1. Initialize Git in the project directory (if not already done):

```bash
cd /home/s4512158/www/djangoapps/learnmore
git init
```

2. Add your files to Git (excluding those in .gitignore):

```bash
git add .
```

3. Make your first commit:

```bash
git commit -m "Initial commit"
```

4. Link to a remote repository (replace with your actual remote repository URL):

```bash
git remote add origin https://github.com/yourusername/learnmore.git
git branch -M main
git push -u origin main
```

## Working with Git

### Daily Development Workflow

1. Pull the latest changes:

```bash
git pull origin main
```

2. Create a new branch for your feature:

```bash
git checkout -b feature/your-feature-name
```

3. Make changes and commit regularly:

```bash
git add .
git commit -m "Describe your changes"
```

4. Push your branch to the remote repository:

```bash
git push origin feature/your-feature-name
```

5. When ready, create a pull request on GitHub to merge your changes into main.

### Best Practices

1. **Never commit sensitive data**: API keys, passwords, etc. should be stored in environment variables or a `.env` file (which is excluded via .gitignore).

2. **Keep commits focused**: Each commit should represent a single logical change.

3. **Write meaningful commit messages**: Good format is a short summary line followed by more detailed explanation if needed.

4. **Pull before pushing**: Always pull the latest changes before pushing to avoid conflicts.

5. **Use branches**: Don't work directly on the main branch.

### What is Excluded

The `.gitignore` file excludes:

- Python virtual environment directories (`venv/`)
- Python cache files (`__pycache__/`, `*.pyc`)
- Database files (`db.sqlite3`)
- Log files and media uploads
- Environment variable files
- IDE-specific files

These exclusions keep the repository clean and avoid storing sensitive or machine-specific information.

## Advanced Git Tips

- To see what files are being ignored: `git status --ignored`
- To temporarily force-add an ignored file: `git add -f filename`
- To see changes before committing: `git diff`
- To discard uncommitted changes: `git checkout -- filename` 