# Pulselytics Database Setup

## Overview
Pulselytics now uses SQLite for secure, encrypted storage of:
- **Client information** (social media profiles)
- **API keys** (encrypted with Fernet symmetric encryption)
- **Scrape history** (audit logs of all scraping operations)
- **Application settings**

## Database Location
- **File**: `backend/pulselytics.db`
- **Encryption Key**: `backend/.encryption_key` ⚠️ **KEEP SECURE - DO NOT SHARE**

## Initial Setup

### 1. Install Dependencies
```powershell
.\venv\Scripts\pip install cryptography google-api-python-client
```

### 2. Initialize Database
```powershell
cd backend
..\venv\Scripts\python database.py
```

This will:
- Create the SQLite database with all tables
- Generate an encryption key for API key storage
- Optionally migrate existing JSON client data

## Database Schema

### Clients Table
Stores client profile information
```sql
CREATE TABLE clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    instagram_username TEXT,
    youtube_channel TEXT,
    twitter_username TEXT,
    facebook_page TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### API Keys Table
Stores encrypted API keys for social media platforms
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    platform TEXT NOT NULL,
    api_key TEXT NOT NULL,           -- Encrypted
    api_secret TEXT,                  -- Encrypted
    access_token TEXT,                -- Encrypted
    refresh_token TEXT,               -- Encrypted
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform)
)
```

### Scrape History Table
Audit log of all scraping operations
```sql
CREATE TABLE scrape_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    posts_fetched INTEGER DEFAULT 0,
    error_message TEXT,
    scrape_method TEXT,
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
)
```

### Settings Table
Application-wide settings
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    data_type TEXT DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Key Encryption

### How It Works
1. **Fernet Encryption**: Uses `cryptography.fernet` for secure symmetric encryption
2. **Encryption Key**: Stored in `backend/.encryption_key` (generated on first run)
3. **Key Masking**: API keys are masked when displayed (e.g., `AIza****xyz`)

### Security Best Practices
✅ **DO:**
- Keep `.encryption_key` file secure
- Add `.encryption_key` to `.gitignore`
- Backup encryption key separately from database
- Use HTTPS in production

❌ **DON'T:**
- Commit encryption key to version control
- Share encryption key publicly
- Store plain-text API keys in frontend

## API Endpoints

### Get All API Keys (Masked)
```http
GET /api/api-keys
```
Returns masked API keys for all platforms.

### Save API Key
```http
POST /api/api-keys/<platform>
Content-Type: application/json

{
  "api_key": "YOUR_API_KEY",
  "api_secret": "OPTIONAL_SECRET",
  "access_token": "OPTIONAL_TOKEN"
}
```
Supported platforms: `youtube`, `facebook`, `instagram`, `twitter`

### Validate API Key
```http
POST /api/api-keys/<platform>/validate
Content-Type: application/json

{
  "api_key": "YOUR_API_KEY"
}
```
Tests the API key against the actual platform API.

### Delete API Key
```http
DELETE /api/api-keys/<platform>
```
Permanently deletes the API key for the specified platform.

## Migration from JSON

### Automatic Migration
When you run `database.py`, it will prompt to migrate existing JSON client files:
```
Migrate existing JSON client data? (y/n): y
```

This will:
- Read all `*.json` files from `backend/data/`
- Extract client information
- Import into SQLite database
- Preserve original JSON files (safe operation)

### Manual Migration
```python
from database import migrate_from_json
migrate_from_json()
```

## Frontend Integration

### APIKeys Page
Located at `/api-keys` in the dashboard:
- **Save Keys**: Enter API keys and save to encrypted database
- **Test Connection**: Validate API keys against real APIs
- **Delete Keys**: Remove API keys from database
- **View Status**: See which platforms have active keys

### API Service (`frontend/src/services/api.js`)
```javascript
import { getApiKeys, saveApiKey, validateApiKey, deleteApiKey } from './services/api';

// Get all saved keys (masked)
const keys = await getApiKeys();

// Save a key
await saveApiKey('youtube', 'AIzaSy...');

// Test a key
const result = await validateApiKey('youtube', 'AIzaSy...');

// Delete a key
await deleteApiKey('youtube');
```

## Legal & Compliance

### Terms of Service Compliance
Users must agree to:
- **YouTube**: [YouTube Terms of Service](https://www.youtube.com/t/terms)
- **Facebook**: [Facebook Platform Terms](https://developers.facebook.com/terms/)
- **Instagram**: [Instagram Platform Policy](https://developers.facebook.com/docs/instagram-platform)
- **Twitter**: [Twitter Developer Agreement](https://developer.twitter.com/en/developer-terms/agreement)

### User Responsibilities
When users enter their own API keys, they:
1. ✅ Own the API keys and accounts
2. ✅ Agree to platform Terms of Service
3. ✅ Are responsible for API quota usage
4. ✅ Can revoke keys at any time
5. ✅ Must follow platform rate limits

### Data Privacy
- API keys are encrypted at rest
- Keys never leave the server in plain text
- Only masked keys shown in frontend
- Users can delete their keys anytime

## Backup & Recovery

### Backup Database
```powershell
# Backup the database file
Copy-Item backend\pulselytics.db backend\pulselytics.db.backup

# Backup the encryption key
Copy-Item backend\.encryption_key backend\.encryption_key.backup
```

### Restore Database
```powershell
# Restore database
Copy-Item backend\pulselytics.db.backup backend\pulselytics.db

# Restore encryption key
Copy-Item backend\.encryption_key.backup backend\.encryption_key
```

⚠️ **IMPORTANT**: Both files must match. If you lose the encryption key, encrypted data cannot be recovered!

## Troubleshooting

### Database Locked Error
```python
sqlite3.OperationalError: database is locked
```
**Solution**: Ensure only one process is accessing the database.

### Decryption Error
```
Decryption error: Invalid token
```
**Solution**: Encryption key doesn't match encrypted data. Restore matching `.encryption_key` file.

### Migration Issues
If migration fails:
1. Check `backend/data/*.json` files exist
2. Verify JSON format is valid
3. Check file permissions
4. Review error logs

## Development vs Production

### Development
- SQLite database file
- Local file-based encryption key
- Single-user mode

### Production (Future)
Consider upgrading to:
- PostgreSQL or MySQL
- Dedicated secret management (AWS KMS, HashiCorp Vault)
- Multi-user support with authentication
- HTTPS only

## Support

For issues or questions:
1. Check error logs: `backend/app.py` logging output
2. Verify database exists: `backend/pulselytics.db`
3. Check encryption key: `backend/.encryption_key`
4. Review this documentation

---

**Last Updated**: November 2025
**Version**: 1.0.0
