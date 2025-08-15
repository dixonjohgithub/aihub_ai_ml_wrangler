# AI Hub Data Wrangler - File Import Interface

A comprehensive file import interface with drag-and-drop functionality, designed to handle Data Wrangler export files with security scanning and data preview capabilities.

## Features

### 🚀 Core Functionality
- **Drag-and-drop file upload** with visual feedback
- **File validation** (size, type, and content checks)
- **Real-time progress tracking** with cancellation support
- **File preview** with data structure analysis
- **Error handling** with user-friendly messages
- **Virus scanning** and security validation
- **Data Wrangler pattern recognition**

### 📊 Supported File Types
- `transformation_file.csv` - Original data transformations
- `mapped_data.csv` - Processed and mapped data
- `metadata.json` - Statistics and configuration files

### 🔒 Security Features
- **Multi-layer file validation**
- **Virus scanning** (ClamAV + fallback scanner)
- **File quarantine** for suspicious content
- **MIME type verification**
- **Content structure validation**

## Quick Start

### Prerequisites
- **Frontend**: Node.js 18+, npm/yarn
- **Backend**: Python 3.10+, pip
- **Optional**: ClamAV for enhanced virus scanning

### Installation

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Architecture

### Frontend Components
```
frontend/src/
├── components/
│   ├── FileDropzone.tsx      # Drag-and-drop interface
│   ├── ProgressTracker.tsx   # Upload progress with controls
│   └── ImportSummary.tsx     # File preview and management
├── services/
│   └── uploadService.ts      # API communication
├── types/
│   └── upload.types.ts       # TypeScript definitions
└── utils/
    └── fileValidation.ts     # Client-side validation
```

### Backend Services
```
backend/app/
├── api/
│   └── upload.py             # REST API endpoints
├── services/
│   ├── file_storage.py       # File management
│   └── virus_scan.py         # Security scanning
└── models/
    └── upload.py             # Data models
```

## API Endpoints

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

Form Data:
- file: [File]
- file_id: [Optional UUID]
- validate_content: [Boolean]
- generate_preview: [Boolean]
- virus_scan: [Boolean]
```

### File Management
- `GET /api/upload/{file_id}/status` - Get upload status
- `GET /api/upload/{file_id}/preview` - Get file preview
- `POST /api/upload/{file_id}/scan` - Trigger virus scan
- `DELETE /api/upload/{file_id}` - Delete file
- `GET /api/upload` - List all uploads
- `GET /api/upload/stats` - Upload statistics

### Validation
- `POST /api/upload/validate` - Validate file without uploading

## Usage Examples

### Basic File Upload
```typescript
import { uploadService } from './services/uploadService';

const uploadFile = async (file: File) => {
  const response = await uploadService.uploadFile(
    file,
    'unique-file-id',
    (progress) => console.log(`Progress: ${progress.percentage}%`)
  );
  
  if (response.success) {
    console.log('Upload successful:', response.data);
  } else {
    console.error('Upload failed:', response.error);
  }
};
```

### File Validation
```typescript
import { validateFile } from './utils/fileValidation';

const validation = validateFile(file);
if (!validation.isValid) {
  console.error('Validation errors:', validation.errors);
}
```

## Configuration

### Environment Variables

#### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
```

#### Backend
```bash
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600  # 100MB
VIRUS_SCAN_ENABLED=true
CLAMAV_PATH=/usr/bin/clamscan
```

### File Size Limits
- **Default**: 100MB per file
- **Configurable** via backend settings
- **Client-side validation** prevents oversized uploads

### Supported MIME Types
- `text/csv`, `application/csv`
- `application/json`, `text/json`
- `text/plain` (for CSV files)

## Development

### Running Tests
```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && pytest
```

### Code Quality
```bash
# Frontend linting
npm run lint

# Backend formatting
black app/
isort app/
```

### Building for Production
```bash
# Frontend
npm run build

# Backend
# Use production WSGI server like Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Security Considerations

### File Validation
- **Multi-layer validation**: Extension, MIME type, content structure
- **Size limits**: Configurable maximum file size
- **Content analysis**: CSV/JSON structure validation

### Virus Scanning
- **Primary**: ClamAV integration (if available)
- **Fallback**: Pattern-based scanning for common threats
- **Quarantine**: Automatic isolation of suspicious files

### Data Protection
- **Temporary storage**: Files initially stored in temp directory
- **Secure deletion**: Proper cleanup of temporary files
- **Access controls**: API-based file access only

## Troubleshooting

### Common Issues

#### Upload Fails with Large Files
- Check file size limits in frontend and backend
- Verify network timeout settings
- Consider chunked upload for very large files

#### Virus Scanner Not Working
- Install ClamAV: `sudo apt-get install clamav clamav-daemon`
- Update definitions: `sudo freshclam`
- Fallback scanner will be used if ClamAV unavailable

#### CORS Errors
- Verify frontend URL in backend CORS settings
- Check API_BASE_URL in frontend configuration

### Log Locations
- **Frontend**: Browser developer console
- **Backend**: Application logs (configurable via logging settings)
- **File operations**: Check upload directory permissions

## Sample Files

The `sample_files/` directory contains example Data Wrangler exports:

- `transformation_file.csv` - Sample employee data
- `mapped_data.csv` - Transformed employee data
- `metadata.json` - Complete transformation metadata

Use these files to test the upload interface and verify functionality.

## Performance

### Optimization Tips
- **Concurrent uploads**: Limited to prevent server overload
- **Progress tracking**: Real-time feedback for user experience
- **Memory management**: Streaming for large file processing
- **Cache**: File previews cached for repeated access

### Monitoring
- Upload statistics available via `/api/upload/stats`
- File processing metrics in metadata
- Error rates and success rates tracked

## License

This project is part of the AI Hub Data Wrangler suite. See the main project LICENSE file for details.

## Support

For issues and feature requests, please refer to the main project repository or contact the development team.