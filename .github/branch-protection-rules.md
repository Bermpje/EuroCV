# GitHub Branch Protection Rules

## Recommended Settings for `main` Branch

To protect the `main` branch, configure these settings on GitHub:

### Navigation
1. Go to: **Settings** → **Branches** → **Add branch protection rule**
2. Branch name pattern: `main`

### Protection Rules

#### ✅ Required Settings
- [x] **Require a pull request before merging**
  - [x] Require approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners (optional)

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Status checks to require:
    - `test` (if GitHub Actions is configured)
    - `lint` (if linting is configured)

- [x] **Require conversation resolution before merging**

- [x] **Require linear history** (recommended for clean git history)

- [x] **Do not allow bypassing the above settings**
  - Applies to administrators: **Yes** (recommended)

#### ⚠️ Optional Settings
- [ ] **Require deployments to succeed before merging** (if using GitHub Deployments)
- [ ] **Lock branch** (only if you want to make it read-only)
- [ ] **Allow force pushes** - **NO** (keep disabled)
- [ ] **Allow deletions** - **NO** (keep disabled)

### Why These Rules?

1. **Pull Request Requirement**: Ensures code review before merging to main
2. **Status Checks**: Automated tests must pass
3. **Conversation Resolution**: All review comments must be addressed
4. **Linear History**: Keeps git history clean and easy to follow
5. **No Force Push**: Prevents accidentally overwriting history
6. **No Deletions**: Prevents accidental branch deletion

### Development Workflow

With these rules in place:
```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and commit
git add .
git commit -m "feat: your changes"

# 3. Push to GitHub
git push origin feature/your-feature

# 4. Create Pull Request on GitHub
# 5. Get review and approval
# 6. Merge via GitHub UI (squash and merge recommended)
```

### Quick Setup Command

Run this in your browser console on the branch protection settings page, or manually check the boxes as described above.

**Note**: Branch protection rules can only be configured through the GitHub web interface, not via git commands.

