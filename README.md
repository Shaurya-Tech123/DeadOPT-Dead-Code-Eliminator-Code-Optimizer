# DeadOPT – Multi-Language Dead Code Optimizer

A production-ready full-stack web platform for analyzing and removing dead code across multiple programming languages.

## Supported Languages
- C
- C++
- Java
- Python

## Features
- 🎨 Modern dark-themed UI with animations
- 📝 Live code editor (Monaco Editor)
- 📤 File upload support
- 🔍 Dead code detection and removal
- 📊 Detailed optimization reports
- 💾 MongoDB history storage
- 👨‍💼 Admin dashboard

## Tech Stack

### Frontend
- React (Vite)
- TailwindCSS
- Monaco Editor
- Axios

### Backend
- Node.js
- Express
- Mongoose
- child_process

### Optimizer Engine
- Python 3.x
- AST parsing
- Regex analysis

## Installation

### Prerequisites
- Node.js (v18+)
- Python 3.8+
- MongoDB (local or cloud)

### Quick Setup (Windows)

1. **Run the setup script:**
   ```powershell
   .\setup.bat
   ```

2. **Or manually:**
   ```powershell
   # Install root dependencies
   npm install

   # Install frontend dependencies
   cd frontend
   npm install
   cd ..

   # Install backend dependencies
   cd backend
   npm install
   cd ..

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```powershell
   # Copy .env.example to .env
   copy .env.example .env
   # Edit .env with your MongoDB URI
   ```

4. **Start MongoDB** (if running locally)

5. **Run the application:**
   ```powershell
   npm run dev
   ```

## Usage

1. Open http://localhost:5173
2. Select your programming language
3. Paste code or upload a file
4. Click "Optimize"
5. View results and download optimized code

## Project Structure

```
DeadOPT/
├── frontend/          # React + Vite frontend
├── backend/           # Express backend
├── optimizer/          # Python optimizer engine
├── package.json       # Root package.json
├── requirements.txt   # Python dependencies
└── setup.bat          # Windows setup script
```

## API Endpoints

- `POST /api/optimize` - Optimize code
- `GET /api/history` - Get optimization history
- `GET /api/admin/logs` - Admin logs (requires auth)

## License

MIT