import React, { useCallback, useRef, useState } from 'react';
import './PhotoUploadZone.css';
import { ACCEPTED_IMAGE_TYPES, MAX_PHOTO_BYTES } from '../../utils/constants';

interface PhotoUploadZoneProps {
  onFileSelected: (file: File) => void;
}

/**
 * Drag-and-drop photo upload zone with preview.
 * Responsibility: file selection and validation only.
 * Does NOT call any API — fires onFileSelected callback to parent.
 */
const PhotoUploadZone: React.FC<PhotoUploadZoneProps> = ({ onFileSelected }) => {
  const [preview, setPreview]     = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSet = useCallback((file: File) => {
    setError(null);
    if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
      setError('Only JPEG, PNG, and WebP images are accepted.');
      return;
    }
    if (file.size > MAX_PHOTO_BYTES) {
      setError(`File too large. Maximum size is ${MAX_PHOTO_BYTES / 1_000_000} MB.`);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    onFileSelected(file);
  }, [onFileSelected]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) validateAndSet(file);
  }, [validateAndSet]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) validateAndSet(file);
  };

  const handleClear = () => {
    setPreview(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="upload-zone-wrapper">
      <div
        className={`upload-zone${isDragging ? ' upload-zone--dragging' : ''}${preview ? ' upload-zone--has-preview' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !preview && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Upload turtle photo"
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      >
        {preview ? (
          <div className="upload-zone__preview">
            <img src={preview} alt="Selected turtle photo" />
            <button
              className="upload-zone__clear"
              onClick={(e) => { e.stopPropagation(); handleClear(); }}
              aria-label="Remove photo"
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="upload-zone__empty">
            <div className="upload-zone__icon" aria-hidden="true">◈</div>
            <p className="upload-zone__title">Drop turtle photo here</p>
            <p className="upload-zone__sub">or click to browse · JPEG, PNG, WebP · max 10 MB</p>
          </div>
        )}
      </div>

      {error && (
        <p className="upload-zone__error" role="alert">{error}</p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_IMAGE_TYPES.join(',')}
        onChange={handleInputChange}
        style={{ display: 'none' }}
        aria-hidden="true"
      />
    </div>
  );
};

export default PhotoUploadZone;
