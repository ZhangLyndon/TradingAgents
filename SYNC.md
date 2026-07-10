## TradingAgents Synchronization

### Remotes

- `upstream`
	- Canonical public repository
	- `git@github.com:TauricResearch/TradingAgents.git`
	- Source of upstream updates

- `origin`
	- Public mirror repository
	- `git@github.com:ZhangLyndon/TradingAgents.git`
	- Destination for synchronized updates

### Instructions

1. Ensure the working tree is clean and switch to the `main` branch.
```bash
git status
git checkout main
```

2. Fetch the latest changes from the upstream repository.
```bash
git fetch upstream
```

3. Merge public upstream changes into the local `main` branch.
```bash
git merge upstream/main
```

4. Resolve merge conflicts if necessary. 

5. Push the synchronized history to the mirror repository.
```bash
git push origin main
```