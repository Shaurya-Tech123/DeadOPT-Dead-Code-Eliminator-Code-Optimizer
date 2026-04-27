import { spawn } from 'child_process';
import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import fs from 'fs';
import mongoose from 'mongoose';
import multer from 'multer';
import path, {
  dirname,
  join,
} from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;
const tempDir = join(__dirname, 'temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir, { recursive: true });
}

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Multer configuration for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 } 
});

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/deadopt', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log(' MongoDB Connected'))
.catch(err => console.error(' MongoDB Connection Error:', err));

// Optimization History Schema
const optimizationSchema = new mongoose.Schema({
  language: { type: String, required: true },
  originalCode: { type: String, required: true },
  optimizedCode: { type: String, required: true },
  linesRemoved: { type: Number, default: 0 },
  report: { type: Object, required: true },
  createdAt: { type: Date, default: Date.now },
  userAgent: String,
});

const Optimization = mongoose.model('Optimization', optimizationSchema);

// Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'DeadOPT API is running' });
});

// Optimize code endpoint
app.post(['/api/optimize', '/optimize'], async (req, res) => {
  try {
    const { code, language } = req.body;

    if (!code || !language) {
      return res.status(400).json({ error: 'Code and language are required' });
    }

    if (!['c', 'cpp', 'java', 'python'].includes(language.toLowerCase())) {
      return res.status(400).json({ error: 'Unsupported language' });
    }

    // Create temporary file
    const extMap = {
      'c': '.c',
      'cpp': '.cpp',
      'java': '.java',
      'python': '.py'
    };

    const tempFile = join(tempDir, `temp-${Date.now()}${extMap[language.toLowerCase()]}`);
    fs.writeFileSync(tempFile, code, 'utf8');

    // Call Python optimizer
    const optimizerPath = join(__dirname, '..', 'optimizer', 'main_optimizer.py');
    const result = await runOptimizer(optimizerPath, language.toLowerCase(), tempFile);

    // Clean up temp file
    fs.unlinkSync(tempFile);

    if (result.error) {
      return res.status(500).json({ error: result.error });
    }

    const optimizationData = {
      language: language.toLowerCase(),
      originalCode: code,
      optimizedCode: result.optimizedCode || code,
      linesRemoved: result.linesRemoved || 0,
      report: result.report || {}
    };

    // Save to MongoDB
    const optimization = new Optimization({
      ...optimizationData,
      userAgent: req.headers['user-agent']
    });
    await optimization.save();

    res.json({
      success: true,
      ...optimizationData,
      symbolTable: result.symbolTable || []
    });

  } catch (error) {
    console.error('Optimization error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Upload file and optimize
app.post('/api/optimize/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const ext = path.extname(req.file.originalname).toLowerCase();

    const langMap = {
      '.c': 'c',
      '.cpp': 'cpp',
      '.cc': 'cpp',
      '.cxx': 'cpp',
      '.java': 'java',
      '.py': 'python'
    };

    const language = langMap[ext];
    if (!language) {
      fs.unlinkSync(filePath);
      return res.status(400).json({ error: 'Unsupported file type' });
    }

    // Call Python optimizer
    const optimizerPath = join(__dirname, '..', 'optimizer', 'main_optimizer.py');
    const result = await runOptimizer(optimizerPath, language, filePath);

    // Clean up uploaded file
    fs.unlinkSync(filePath);

    if (result.error) {
      return res.status(500).json({ error: result.error });
    }

    const optimizationData = {
      language: language,
      originalCode: fileContent,
      optimizedCode: result.optimizedCode || fileContent,
      linesRemoved: result.linesRemoved || 0,
      report: result.report || {}
    };

    // Save to MongoDB
    const optimization = new Optimization({
      ...optimizationData,
      userAgent: req.headers['user-agent']
    });
    await optimization.save();

    res.json({
      success: true,
      ...optimizationData,
      symbolTable: result.symbolTable || []
    });

  } catch (error) {
    console.error('Upload optimization error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Get optimization history
app.get('/api/history', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const optimizations = await Optimization.find()
      .sort({ createdAt: -1 })
      .limit(limit)
      .select('-originalCode -optimizedCode'); // Exclude large fields

    res.json({ success: true, data: optimizations });
  } catch (error) {
    console.error('History error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get(['/history', '/api/admin/logs'], async (req, res) => {
  try {
    const query = Optimization.find().sort({ createdAt: -1 });
    if (req.query.limit) {
      query.limit(parseInt(req.query.limit));
    }
    const optimizations = await query;
    res.json({ success: true, data: optimizations });
  } catch (error) {
    console.error('History logs error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/history/:id', async (req, res) => {
  try {
    const deleted = await Optimization.findByIdAndDelete(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: 'History item not found' });
    }
    return res.json({ success: true, message: 'History item deleted successfully' });
  } catch (error) {
    console.error('Delete history error:', error);
    return res.status(500).json({ error: 'Failed to delete history item' });
  }
});

// Helper function to run Python optimizer
function runOptimizer(optimizerPath, language, filePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [optimizerPath, language, filePath]);
    
    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject({ error: `Optimizer failed: ${stderr || 'Unknown error'}` });
        return;
      }

      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (parseError) {
        reject({ error: `Failed to parse optimizer output: ${stdout}` });
      }
    });

    pythonProcess.on('error', (error) => {
      reject({ error: `Failed to start optimizer: ${error.message}` });
    });
  });
}

// Start server
app.listen(PORT, () => {
  console.log(`🚀 DeadOPT Backend running on http://localhost:${PORT}`);
});