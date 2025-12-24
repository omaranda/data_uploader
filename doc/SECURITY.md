# Security Best Practices

This document outlines security measures implemented in this project to protect sensitive information.

## Protected Secrets

### ✅ What is Protected (NOT in Git)

The following sensitive information is **gitignored** and will NOT be committed:

1. **`.env`** - Contains all secrets:
   - `MADXXX_API_KEY` - Your API authentication key
   - `MADXXX_API_URL` - Your private API endpoint URL
   - `DB_PASSWORD` - Database password

2. **`config_files/*.json`** - May contain sensitive paths and configurations
   - Exception: `config_files/example_config.json` is tracked as a template

3. **Logs** - May contain sensitive runtime information
   - `logs/` directory
   - `*.log` files

### ✅ What is Safe to Commit

These files are safe and should be tracked:

1. **`.env.example`** - Template with placeholder values
2. **`config_files/example_config.json`** - Example configuration
3. **`config_files/job_config.json`** - Job templates (no secrets, just structure)
4. **All source code** - Contains no hardcoded secrets

## Security Implementations

### 1. No Hardcoded Secrets

✅ **BEFORE (Insecure):**
```python
# DON'T DO THIS
api_key = "pVEoLsguuoY6D3P!ksfj-EuAzARe*EDv"  # ❌ Exposed in code
endpoint = "https://secret-endpoint.com/api"    # ❌ Exposed in code
```

✅ **AFTER (Secure):**
```python
# DO THIS
api_key = os.getenv('MADXXX_API_KEY')           # ✅ From .env
endpoint = os.getenv('MADXXX_API_URL')          # ✅ From .env

if not api_key or not endpoint:
    raise ValueError("Required environment variables not set")
```

### 2. Required Environment Variables

The application will **fail early** if secrets are missing:

```bash
❌ No API key provided. Use --api-key, MADXXX_API_KEY env var, or job config
❌ No endpoint URL provided. Set MADXXX_API_URL in .env, use --endpoint-url, or configure in job_config.json
```

### 3. Environment Variable Priority

Configuration follows this priority (highest to lowest):

1. **CLI flags** (temporary, for testing)
2. **Environment variables** (`.env` file) ← **Recommended**
3. **Config files** (job_config.json endpoints)
4. ~~Hardcoded defaults~~ (removed for security)

## Setup Instructions

### First Time Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual secrets:**
   ```bash
   # .env file (DO NOT COMMIT THIS)
   MADXXX_API_KEY=your-actual-api-key-here
   MADXXX_API_URL=https://your-actual-endpoint.com/api/v1/madxxx_tasks/job
   ```

3. **Verify `.env` is gitignored:**
   ```bash
   git status
   # .env should NOT appear in the list
   ```

### For Team Members

When sharing this project with team members:

1. Share `.env.example` (already in git)
2. **DO NOT** share your `.env` file
3. Each team member creates their own `.env` with their credentials
4. Document the required values in `.env.example`

## Accidental Exposure Prevention

### If You Accidentally Committed Secrets

If you accidentally commit `.env` or other secrets:

1. **Immediately rotate/change the exposed credentials**
2. **Remove from git history:**
   ```bash
   # Remove file from git history (use with caution!)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (WARNING: affects all team members)
   git push origin --force --all
   ```

3. **Use git-secrets or similar tools** to prevent future accidents:
   ```bash
   # Install git-secrets
   brew install git-secrets  # macOS

   # Setup
   git secrets --install
   git secrets --register-aws
   ```

### `.gitignore` Verification

Current `.gitignore` protects:

```gitignore
# Environment variables
.env                    ✅ Protected

# Config files (may contain sensitive data)
config_files/*.json     ✅ Protected (except example)
!config_files/example_config.json  ✅ Template is tracked

# Logs
logs/                   ✅ Protected
*.log                   ✅ Protected
```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MADXXX_API_KEY` | API authentication key | `pVEoLsguuoY6D3P!...` |
| `MADXXX_API_URL` | API endpoint URL | `https://wm2drzie9x...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `data_uploader` |
| `DB_USER` | Database user | `uploader` |
| `DB_PASSWORD` | Database password | `uploader_pass` |
| `LOG_LEVEL` | Logging level | `INFO` |

## CI/CD Integration

When setting up CI/CD pipelines:

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
env:
  MADXXX_API_KEY: ${{ secrets.MADXXX_API_KEY }}
  MADXXX_API_URL: ${{ secrets.MADXXX_API_URL }}
```

Add secrets in: **Repository Settings → Secrets and variables → Actions**

### Docker Deployment

```bash
# Pass environment variables to container
docker run -d \
  --env-file .env \
  data-uploader:latest
```

## Security Checklist

Before committing code:

- [ ] No hardcoded API keys in source code
- [ ] No hardcoded URLs in source code
- [ ] `.env` file is gitignored
- [ ] `.env.example` has placeholder values only
- [ ] Sensitive config files are gitignored
- [ ] All secrets loaded from environment variables
- [ ] Error messages don't expose secrets
- [ ] Logs don't contain secrets (API keys, URLs)

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email the maintainer directly
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Additional Resources

- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [12 Factor App: Config](https://12factor.net/config)
