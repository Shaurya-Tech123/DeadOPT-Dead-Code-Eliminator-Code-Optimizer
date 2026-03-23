# DeadOPT Installation Guide

## Complete Installation Instructions

### Step 1: Verify Prerequisites

```powershell
# Check Node.js version (should be 18+)
node --version

# Check Python version (should be 3.8+)
python --version

# Check if MongoDB is installed
mongod --version
```

### Step 2: Clone/Create Project

The project is already in `E:\DeadOPT`. If you need to recreate it, ensure the folder structure matches the README.

### Step 3: Install Dependencies

#### Automated (Recommended):
```powershell
cd E:\DeadOPT
.\setup.bat
```

#### Manual Installation:

**Root Dependencies:**
```powershell
cd E:\DeadOPT
npm install
```

**Frontend Dependencies:**
```powershell
cd E:\DeadOPT\frontend
npm install
cd ..
```

**Backend Dependencies:**
```powershell
cd E:\DeadOPT\backend
npm install
cd ..
```

**Python Dependencies:**
```powershell
cd E:\DeadOPT
pip install -r requirements.txt
```

### Step 4: Configure Environment

1. Create `.env` file from example:
   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` file with your settings:
   ```
   MONGODB_URI=mongodb://localhost:27017/deadopt
   PORT=5000
   NODE_ENV=development
   FRONTEND_URL=http://localhost:5173
   ```

### Step 5: Start MongoDB

**Option A: Local MongoDB Service**
- If MongoDB is installed as a Windows service, it should start automatically
- Verify it's running: Check Services (services.msc) for "MongoDB"

**Option B: Manual Start**
```powershell
# Navigate to MongoDB bin directory (adjust path as needed)
cd "C:\Program Files\MongoDB\Server\7.0\bin"
mongod --dbpath "C:\data\db"
```

**Option C: MongoDB Atlas (Cloud)**
- Create free account at https://www.mongodb.com/cloud/atlas
- Get connection string
- Update MONGODB_URI in .env file

### Step 6: Start the Application

```powershell
cd E:\DeadOPT
npm run dev
```

This command uses `concurrently` to run both frontend and backend:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

### Step 7: Verify Installation

1. Open browser to http://localhost:5173
2. You should see the DeadOPT landing page
3. Click "Get Started"
4. Try optimizing a simple code snippet

## Troubleshooting

### Issue: "Cannot find module"
**Solution:** Ensure you've run `npm install` in all three directories (root, frontend, backend)

### Issue: "MongoDB connection failed"
**Solutions:**
- Verify MongoDB is running
- Check MONGODB_URI in .env file
- For local MongoDB, ensure it's listening on port 27017
- For cloud MongoDB, verify connection string is correct

### Issue: "Port already in use"
**Solutions:**
- Change PORT in .env file (backend)
- Change port in frontend/vite.config.js (frontend)
- Or stop the process using the port

### Issue: "Python optimizer not found"
**Solutions:**
- Verify Python is in PATH: `python --version`
- Reinstall Python dependencies: `pip install -r requirements.txt`
- Check that optimizer files exist in `optimizer/` directory

### Issue: "Module 'astunparse' not found"
**Solution:**
```powershell
pip install astunparse
```

## Development Commands

```powershell
# Run both frontend and backend
npm run dev

# Run only backend
npm run server

# Run only frontend
npm run client

# Build frontend for production
npm run build

# Start production server
npm start
```

## File Structure Verification

After installation, verify this structure exists:

```
DeadOPT/
├── frontend/
│   ├── node_modules/          (created after npm install)
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── OptimizerPage.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/
│   ├── node_modules/          (created after npm install)
│   ├── server.js
│   └── package.json
├── optimizer/
│   ├── main_optimizer.py
│   ├── python_optimizer.py
│   ├── c_optimizer.py
│   ├── cpp_optimizer.py
│   └── java_optimizer.py
├── node_modules/               (created after npm install)
├── package.json
├── requirements.txt
├── setup.bat
├── README.md
├── QUICKSTART.md
└── .env                        (create from .env.example)
```

## Next Steps

1. ✅ Installation complete
2. ✅ Start the application
3. ✅ Test with sample code
4. ✅ Explore the admin dashboard
5. ✅ Customize as needed

## Production Deployment

For production deployment:

1. Build frontend:
   ```powershell
   cd frontend
   npm run build
   ```

2. Set NODE_ENV=production in .env

3. Use a process manager like PM2:
   ```powershell
   npm install -g pm2
   pm2 start backend/server.js
   ```

4. Configure reverse proxy (nginx/Apache) if needed

5. Set up MongoDB replica set for production

## Support

Refer to README.md and QUICKSTART.md for more information.