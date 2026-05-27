

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadSAP, uploadUtility, uploadTravel } from '../api/ingestion';
import styles from './UploadPage.module.css';

function UploadCard({ label, desc, onUpload, loading, success, error, onFileChange, file }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardTitle}>{label}</div>
      <div className={styles.cardDesc}>{desc}</div>
      <form
        className={styles.inputRow}
        onSubmit={e => {
          e.preventDefault();
          onUpload();
        }}
        autoComplete="off"
      >
        <input
          className={styles.fileInput}
          type="file"
          onChange={onFileChange}
          disabled={loading}
        />
        <button
          className={styles.button}
          type="submit"
          disabled={!file || loading}
        >
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      <div className={styles.feedback}>
        {success && <span className={styles.success}>Upload successful!</span>}
        {error && <span className={styles.error}>{error}</span>}
      </div>
    </div>
  );
}

const UploadPage = () => {
  const navigate = useNavigate();

  // SAP
  const [sapFile, setSapFile] = useState(null);
  const [sapLoading, setSapLoading] = useState(false);
  const [sapSuccess, setSapSuccess] = useState(false);
  const [sapError, setSapError] = useState('');

  // Utility
  const [utilityFile, setUtilityFile] = useState(null);
  const [utilityLoading, setUtilityLoading] = useState(false);
  const [utilitySuccess, setUtilitySuccess] = useState(false);
  const [utilityError, setUtilityError] = useState('');

  // Travel
  const [travelFile, setTravelFile] = useState(null);
  const [travelLoading, setTravelLoading] = useState(false);
  const [travelSuccess, setTravelSuccess] = useState(false);
  const [travelError, setTravelError] = useState('');

  // Handlers
  const handleUpload = async (type) => {
    let file, setLoading, setSuccess, setError, uploadFn, setFile;
    if (type === 'sap') {
      file = sapFile;
      setLoading = setSapLoading;
      setSuccess = setSapSuccess;
      setError = setSapError;
      uploadFn = uploadSAP;
      setFile = setSapFile;
    } else if (type === 'utility') {
      file = utilityFile;
      setLoading = setUtilityLoading;
      setSuccess = setUtilitySuccess;
      setError = setUtilityError;
      uploadFn = uploadUtility;
      setFile = setUtilityFile;
    } else {
      file = travelFile;
      setLoading = setTravelLoading;
      setSuccess = setTravelSuccess;
      setError = setTravelError;
      uploadFn = uploadTravel;
      setFile = setTravelFile;
    }
    setLoading(true);
    setSuccess(false);
    setError('');
    try {
      await uploadFn(file);
      setSuccess(true);
      setFile(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.uploadBg}>
      <div className={styles.title}>Enterprise ESG Data Ingestion</div>
      <div className={styles.subtitle}>Upload and review operational sustainability datasets</div>
      <div className={styles.cards}>
        <UploadCard
          label="SAP Fuel / Procurement"
          desc="Fuel and procurement operational exports"
          file={sapFile}
          loading={sapLoading}
          success={sapSuccess}
          error={sapError}
          onFileChange={e => {
            setSapFile(e.target.files[0]);
            setSapSuccess(false);
            setSapError('');
          }}
          onUpload={() => handleUpload('sap')}
        />
        <UploadCard
          label="Utility Electricity"
          desc="Facility electricity consumption records"
          file={utilityFile}
          loading={utilityLoading}
          success={utilitySuccess}
          error={utilityError}
          onFileChange={e => {
            setUtilityFile(e.target.files[0]);
            setUtilitySuccess(false);
            setUtilityError('');
          }}
          onUpload={() => handleUpload('utility')}
        />
        <UploadCard
          label="Corporate Travel"
          desc="Corporate travel activity exports"
          file={travelFile}
          loading={travelLoading}
          success={travelSuccess}
          error={travelError}
          onFileChange={e => {
            setTravelFile(e.target.files[0]);
            setTravelSuccess(false);
            setTravelError('');
          }}
          onUpload={() => handleUpload('travel')}
        />
      </div>
      <button
        className={styles.dashboardBtn}
        onClick={() => navigate('/dashboard')}
      >
        Go to Dashboard
      </button>
    </div>
  );
};

export default UploadPage;
