# DeadOPT Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Node.js (v18 or higher) - Check with: `node --version`
- ✅ Python 3.8+ - Check with: `python --version`
- ✅ MongoDB running (local or cloud connection string)

## Installation Steps

### Option 1: Automated Setup (Windows)

```powershell
cd E:\DeadOPT
.\setup.bat
```

### Option 2: Manual Setup

```powershell
# 1. Install root dependencies
npm install

# 2. Install frontend dependencies
cd frontend
npm install
cd ..

# 3. Install backend dependencies
cd backend
npm install
cd ..

# 4. Install Python dependencies
pip install -r requirements.txt
```

## Configuration

1. **Create .env file:**
   ```powershell
   copy .env.example .env
   ```

2. **Edit .env file** with your MongoDB URI:
   ```
   MONGODB_URI=mongodb://localhost:27017/deadopt
   PORT=5000
   NODE_ENV=development
   FRONTEND_URL=http://localhost:5173
   ```

## Starting the Application

### Start MongoDB (if running locally)
```powershell
# If MongoDB is installed as a service, it should start automatically
# Otherwise, start it manually:
mongod
```

### Start the Application
```powershell
# From the root directory (E:\DeadOPT)
npm run dev
```

This will start:
- Frontend on http://localhost:5173
- Backend on http://localhost:5000

## Testing the Application

1. Open http://localhost:5173 in your browser
2. Click "Get Started"
3. Select a language (Python, C, C++, or Java)
4. Paste some code or upload a file
5. Click "Optimize"
6. View the results!

## Example Test Code

### Python Example:
```python
def unused_function():
    return 42

x = 10
y = 20
z = x + y

if False:
    print("This will be removed")

def main():
    print("Hello, World!")
    return z

if __name__ == "__main__":
    main()
```

### C Example:
```c
#include <stdio.h>

int unused_var = 5;

int main() {
    int x = 10;
    int y = 20;
    int z = x + y;
    
    if (0) {
        printf("This will be removed");
    }
    
    return 0;
}
```

## Troubleshooting

### Port Already in Use
If port 5000 or 5173 is already in use:
- Change PORT in .env file
- Change port in frontend/vite.config.js

### MongoDB Connection Error
- Ensure MongoDB is running
- Check MONGODB_URI in .env file
- For cloud MongoDB, use connection string format:
  `mongodb+srv://username:password@cluster.mongodb.net/deadopt`

### Python Optimizer Not Working
- Ensure Python is in PATH
- Verify requirements.txt packages are installed:
  ```powershell
  pip install -r requirements.txt
  ```

### Module Not Found Errors
- Run `npm install` in root, frontend, and backend directories
- Clear node_modules and reinstall if needed

## Project Structure

```
DeadOPT/
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── OptimizerPage.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── backend/           # Express backend
│   ├── server.js
│   └── package.json
├── optimizer/          # Python optimizer engine
│   ├── main_optimizer.py
│   ├── python_optimizer.py
│   ├── c_optimizer.py
│   ├── cpp_optimizer.py
│   └── java_optimizer.py
├── package.json       # Root package.json
├── requirements.txt   # Python dependencies
└── setup.bat          # Windows setup script
```

## Next Steps

- Customize the UI in `frontend/src/components/`
- Add more optimization rules in `optimizer/*_optimizer.py`
- Extend API endpoints in `backend/server.js`
- Add authentication for admin dashboard
- Deploy to production!

## Support

For issues or questions, check the main README.md file.