# Railway Deployment Configuration

## Environment Setup

### Production Environment (main branch)
- **Branch**: `main`
- **URL**: api.domainchecker.raposa.tech
- **Auto-deploy**: Enabled on push to main
- **Environment variables**: Production settings

### Development Environment (develop branch)  
- **Branch**: `develop`
- **URL**: stage.domainchecker.raposa.tech
- **Auto-deploy**: Enabled on push to develop
- **Environment variables**: Development settings

## Branching Strategy

```
main (production)
├── develop (staging)
    ├── feature/email-templates
    ├── feature/new-feature
    └── bugfix/fix-something
```

## Workflow

1. **Create feature branches** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Work on your feature** and commit changes:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

3. **Merge to develop** for testing:
   ```bash
   git checkout develop
   git merge feature/your-feature-name
   git push origin develop
   # This triggers deployment to stage.domainchecker.raposa.tech
   ```

4. **Merge to main** for production:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   # This triggers deployment to api.domainchecker.raposa.tech
   ```

## Railway Configuration

### To connect production to main branch:
```bash
railway environment use production
railway service connect --branch main
```

### To connect development to develop branch:
```bash
railway environment use development  
railway service connect --branch develop
```

## Environment Variables

Make sure both environments have:
- `DATABASE_URL` (separate databases)
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL`
- Any other production secrets

## Database Migration Strategy

- **Development**: Uses `create_all()` when `ENVIRONMENT=development`
- **Production**: Uses Alembic migrations automatically
