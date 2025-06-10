import React, { useState } from 'react';
import { Upload, X, FileText, Image, File, Eye } from 'lucide-react';

const FileUpload = ({ 
  label = "Upload Files", 
  description = "Upload images, documents, or test results",
  acceptedFormats = "image/*,.pdf,.doc,.docx",
  maxFiles = 5,
  maxSizeMB = 10,
  onFilesChange,
  existingFiles = []
}) => {
  const [files, setFiles] = useState(existingFiles);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file) => {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File ${file.name} exceeds ${maxSizeMB}MB limit`;
    }
    return null;
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError('');

    const droppedFiles = [...e.dataTransfer.files];
    handleFiles(droppedFiles);
  };

  const handleFileInput = (e) => {
    const selectedFiles = [...e.target.files];
    handleFiles(selectedFiles);
  };

  const handleFiles = (newFiles) => {
    const totalFiles = files.length + newFiles.length;
    
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const validatedFiles = [];
    const errors = [];

    newFiles.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        // Create preview URL for images
        const fileObj = {
          id: Date.now() + Math.random(),
          file: file,
          name: file.name,
          size: file.size,
          type: file.type,
          url: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
        };
        validatedFiles.push(fileObj);
      }
    });

    if (errors.length > 0) {
      setError(errors.join(', '));
    } else {
      const updatedFiles = [...files, ...validatedFiles];
      setFiles(updatedFiles);
      if (onFilesChange) {
        onFilesChange(updatedFiles);
      }
    }
  };

  const removeFile = (fileId) => {
    const updatedFiles = files.filter(f => f.id !== fileId);
    setFiles(updatedFiles);
    if (onFilesChange) {
      onFilesChange(updatedFiles);
    }
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) return <Image className="w-5 h-5" />;
    if (fileType.includes('pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    return <File className="w-5 h-5" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      
      {/* Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
          dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept={acceptedFormats}
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            {description}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Drag and drop or click to browse
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Max {maxFiles} files, up to {maxSizeMB}MB each
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((fileObj) => (
            <div
              key={fileObj.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {getFileIcon(fileObj.type)}
                <div>
                  <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                    {fileObj.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(fileObj.size)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {fileObj.url && (
                  <button
                    type="button"
                    onClick={() => window.open(fileObj.url, '_blank')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => removeFile(fileObj.id)}
                  className="p-1 text-red-400 hover:text-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;