# Project Configuration & Deployment Details

## Repository Information
- **Repo Name:** localnewsagent
- **GitHub Owner:** mohamadhassoun1
- **GitHub URL:** https://github.com/mohamadhassoun1/localnewsagent
- **Current Branch:** main
- **Render Live URL:** https://localnewsagent.onrender.com/

---

## Environment Variables & Secrets

### Local Development (.env.local)
```
GEMINI_API_KEY=PLACEHOLDER_API_KEY
```
**Note:** Replace `PLACEHOLDER_API_KEY` with your actual Google Gemini API key

### Render Deployment Environment Variables
Set these in Render Dashboard → Settings → Environment:
```
GEMINI_API_KEY=<your-actual-gemini-key>
PUBLISH_TOKEN=<your-publish-token>
NODE_ENV=production
PORT=8080
```

**Critical Secrets:**
- `GEMINI_API_KEY` - Google AI API key (keep private)
- `PUBLISH_TOKEN` - Token for protecting /publish endpoint

---

## Files & Configuration

### Root Level Files
| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage Docker build (frontend + backend) |
| `.env.local` | Local development environment variables |
| `.gitignore` | Git ignore patterns |
| `package.json` | Frontend (Vite + React) dependencies |
| `vite.config.ts` | Vite build configuration |
| `tsconfig.json` | TypeScript configuration |
| `index.html` | HTML entry point |
| `App.tsx` | Main React component |
| `index.tsx` | React DOM render |
| `types.ts` | TypeScript type definitions |
| `README.md` | Project documentation |

### Backend Files
| File | Purpose |
|------|---------|
| `backend/index.js` | Express server (port 8080) |
| `backend/package.json` | Backend dependencies |

### Directories
| Directory | Purpose |
|-----------|---------|
| `components/` | React components |
| `utils/` | Utility functions |
| `data/` | Data files |
| `.git/` | Git repository |

---

## Git Commits (Recent)
```
40e3a1a - Simplify Dockerfile: remove --silent and use npm install
b3f50aa - Fix backend dependencies: make @google/genai optional
6f2c66a - Fix npm install flag in Dockerfile
a900d1b - Add Dockerfile and serve built frontend from backend
03aae3c - Replace project with Majid Al Futtaim app from archive
a751ffb - Add Render deployment configuration (backup-before-replace branch)
652f89d - Add GitHub push script and deployment instructions
6030623 - LocalNewsAgent v1.0 - Autonomous local news publishing system
```

---

## Build & Deployment Configuration

### Dockerfile Overview
- **Stage 1 (Builder):** Builds Vite frontend (`npm run build`)
- **Stage 2 (Runner):** Runs Express backend serving frontend
- **Base Image:** Node 18-Alpine
- **Port:** 8080
- **Entry Point:** `node backend/index.js`

### Frontend (Vite + React)
- **Dev Command:** `npm run dev`
- **Build Command:** `npm run build`
- **Preview Command:** `npm run preview`
- **Port (dev):** 3000
- **Output:** `dist/` folder

### Backend (Express)
- **Start Command:** `node backend/index.js`
- **Port:** 8080 (reads from `process.env.PORT`)
- **Features:** 
  - Serves frontend static files from `dist/`
  - API endpoints for inventory management
  - AI integration (Google Gemini)
  - CORS enabled
  - Authentication middleware

---

## Dependencies

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@google/genai": "latest"
  },
  "devDependencies": {
    "@types/node": "^22.14.0",
    "@vitejs/plugin-react": "^5.0.0",
    "typescript": "~5.8.2",
    "vite": "^6.2.0"
  }
}
```

### Backend (backend/package.json)
```json
{
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2"
  },
  "optionalDependencies": {
    "@google/genai": "^0.1.3"
  }
}
```

---

## Render Service Settings

### Service Type
- **Service Name:** localnewsagent
- **Runtime:** Docker
- **Build Command:** (uses Dockerfile)
- **Start Command:** (uses Dockerfile CMD)

### Environment Configuration
Set these variables in Render Dashboard:
1. `GEMINI_API_KEY` - Your Google API key
2. `PUBLISH_TOKEN` - Your publish endpoint token
3. `NODE_ENV` - Set to `production`
4. `PORT` - Set to `8080`

---

## GitHub Push Information

### Remote Configuration
```
origin https://github.com/mohamadhassoun1/localnewsagent.git (fetch)
origin https://github.com/mohamadhassoun1/localnewsagent.git (push)
```

### Branches
- `main` - Production branch (deployed to Render)
- `backup-before-replace` - Backup of original LocalNewsAgent code

### Push Commands
```powershell
# Stage and commit changes
git add .
git commit -m "your message"

# Push to main
git push origin main

# Force push if needed (use carefully)
git push -f origin main
```

---

## Local Development

### Setup
```powershell
cd c:\Users\moham\Desktop\blog

# Install dependencies
npm install

# Create .env.local with your keys
echo "GEMINI_API_KEY=your-key" > .env.local
```

### Run Locally
```powershell
# Terminal 1 - Frontend dev server
npm run dev

# Terminal 2 - Backend server
cd backend
npm start
```

### Docker Build & Run Locally
```powershell
# Build image
docker build -t localnewsagent:latest .

# Run container
docker run -p 8080:8080 ^
  -e GEMINI_API_KEY=your-key ^
  -e NODE_ENV=production ^
  localnewsagent:latest
```

---

## Important Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| Frontend (dev) | 3000 | http://localhost:3000 |
| Backend | 8080 | http://localhost:8080 |
| Render (production) | 443 | https://localnewsagent.onrender.com |

---

## Key Features

### Backend API Endpoints
- `POST /login` - Authentication
- `GET /data/all` - Get all data
- `GET /data/store` - Get store data
- `POST /items/add` - Add inventory item
- `PUT /items/:itemId` - Update item
- `POST /items/:itemId/delete` - Delete item
- `POST /admin/staff` - Add staff (admin only)
- `POST /admin/codes/:code/delete` - Delete access code (admin only)
- `POST /ai/ask` - AI query endpoint

### Frontend Features
- Inventory tracking system
- Expiration date monitoring
- Staff management
- Store access codes
- AI-powered queries

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env.local` to git (already in `.gitignore`)
- `PUBLISH_TOKEN` should be kept secret
- `GEMINI_API_KEY` should be kept secret
- Use environment variables, not hardcoded values
- The authentication in `backend/index.js` uses hardcoded admin email - change this for production

---

## Troubleshooting

### Build Fails on Render
1. Check Render build logs for specific errors
2. Ensure `GEMINI_API_KEY` is set in Render environment
3. Verify Dockerfile is present in repo root
4. Check Node version compatibility (Node 18+)

### App Won't Start
1. Check `backend/index.js` syntax
2. Verify PORT environment variable is set
3. Check for port conflicts (8080 should be free)
4. Ensure all dependencies installed correctly

### Frontend Not Loading
1. Verify `dist/` folder is created during build
2. Check if `backend/index.js` static serving is configured
3. Verify `index.html` path in serving configuration

---

## Next Steps for Production

1. ✅ Update `.env.local` with real `GEMINI_API_KEY`
2. ✅ Set `PUBLISH_TOKEN` in Render environment
3. ✅ Test app on https://localnewsagent.onrender.com
4. ✅ Monitor Render logs for errors
5. ✅ Set up error tracking (optional: Sentry, LogRocket)
6. ✅ Configure custom domain (optional)

