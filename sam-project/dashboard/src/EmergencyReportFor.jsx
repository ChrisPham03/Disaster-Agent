import React, { useState } from 'react';

const EmergencyReportForm = ({ onSuccess, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    emergencyType: '',
    description: '',
    location: '',
    latitude: null,
    longitude: null,
    numPeople: 1,
  });

  const [locationStatus, setLocationStatus] = useState('idle'); // idle, loading, success, error
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  // --- VALIDATION ---
  const validateForm = () => {
    const errors = {};
     
    // Check if we have EITHER a text location OR coordinates
    if (!formData.location.trim() && (!formData.latitude || !formData.longitude)) {
      errors.location = 'Location or coordinates required';
    }
    
    if (!formData.numPeople || formData.numPeople < 1) {
      errors.numPeople = 'Number of people must be at least 1';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // --- FEATURE 1: GET COORDINATES FROM TEXT (e.g. "Ottawa") ---
  const handleAddressSearch = async () => {
    if (!formData.location.trim()) {
      setError('Please type a city or address first (e.g., "Ottawa")');
      return;
    }

    setLocationStatus('loading');
    setError(null);

    try {
      // Using OpenStreetMap (Nominatim) - Free API
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(formData.location)}`
      );
      
      if (!response.ok) throw new Error('Network error');
      
      const data = await response.json();

      if (data && data.length > 0) {
        const result = data[0];
        const lat = parseFloat(result.lat);
        const lon = parseFloat(result.lon);

        setFormData(prev => ({
          ...prev,
          latitude: lat,
          longitude: lon,
          // Optional: Update text to the official full address found
          // location: result.display_name 
        }));
        setLocationStatus('success');
      } else {
        setError('Location not found. Try a more specific address.');
        setLocationStatus('error');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to search address. Check your internet connection.');
      setLocationStatus('error');
    }
  };

  // --- FEATURE 2: GET BROWSER GPS ---
  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setLocationStatus('loading');
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        setFormData(prev => ({
          ...prev,
          latitude: lat,
          longitude: lng,
          location: `GPS Detected: ${lat.toFixed(4)}, ${lng.toFixed(4)}`
        }));
        
        setLocationStatus('success');
        setError(null);
      },
      (error) => {
        let errorMsg = '';
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = 'Location blocked. Please enable permissions in browser settings or type address manually.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMsg = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            errorMsg = 'Location request timed out.';
            break;
          default:
            errorMsg = 'An unknown error occurred.';
        }
        setError(errorMsg);
        setLocationStatus('error');
      }
    );
  };

  // --- SUBMIT ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setError('Please fix the validation errors');
      return;
    }
    
    setSubmitting(true);
    setError(null);

    try {
      const API_BASE_URL = 'http://localhost:5050';
      
      const payload = {
        location: formData.location,
        latitude: formData.latitude,
        longitude: formData.longitude,
        description: `[${formData.emergencyType.toUpperCase()}] ${formData.description}${formData.name ? ` | Reporter: ${formData.name}` : ''}${formData.phone ? ` | Contact: ${formData.phone}` : ''}`,
        num_people: parseInt(formData.numPeople),
        reporter_contact: formData.phone,
      };

      const response = await fetch(`${API_BASE_URL}/api/victim/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      if (result.status === 'success' || result.victim_id) {
        if (onSuccess) {
          onSuccess(result);
        }
        // Reset form
        setFormData({
          name: '',
          phone: '',
          emergencyType: '',
          description: '',
          location: '',
          latitude: null,
          longitude: null,
          numPeople: 1,
        });
        setLocationStatus('idle');
      } else {
        setError(result.message || 'Failed to submit report');
      }
    } catch (err) {
      console.error('Submit error:', err);
      setError(`Failed to submit report: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.container}>
        <div style={styles.header}>
          <div style={styles.headerContent}>
            <div style={styles.headerIcon}>🚨</div>
            <div>
              <h2 style={styles.title}>EMERGENCY REPORT</h2>
              <p style={styles.subtitle}>PROVIDE SITUATION DETAILS</p>
            </div>
          </div>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>

        <div style={styles.alertBanner}>
          <span>⚠️</span>
          <span>All reports are logged and prioritized by severity</span>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGrid}>
        
            <div style={styles.formGroup}>
              <label style={styles.label}>
                CONTACT NUMBER <span style={styles.optional}>*</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 (555) 123-4567"
                style={{
                  ...styles.input,
                  ...(validationErrors.phone ? styles.inputError : {})
                }}
              />
              {validationErrors.phone && (
                <span style={styles.errorText}>{validationErrors.phone}</span>
              )}
            </div>
          </div>


          <div style={styles.formGroup}>
            <label style={styles.label}>
              SITUATION DESCRIPTION <span style={styles.optional}>*</span>
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the emergency in detail..."
              style={{
                ...styles.textarea,
                ...(validationErrors.description ? styles.inputError : {})
              }}
            />
            {validationErrors.description && (
              <span style={styles.errorText}>{validationErrors.description}</span>
            )}
            <div style={styles.charCount}>
              {formData.description.length} characters
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>
              NUMBER OF PEOPLE AFFECTED <span style={styles.optional}>*</span>
            </label>
            <input
              type="number"
              name="numPeople"
              value={formData.numPeople}
              onChange={handleChange}
              min="1"
              style={{
                ...styles.input,
                ...(validationErrors.numPeople ? styles.inputError : {})
              }}
            />
          </div>

          {/* UPDATED LOCATION SECTION */}
          <div style={styles.formGroup}>
            <label style={styles.label}>
              LOCATION <span style={styles.required}>*</span>
            </label>
            <div style={styles.locationGroup}>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="Type 'Ottawa', Address, or Landmark"
                style={{
                  ...styles.input,
                  flex: 1,
                  ...(validationErrors.location ? styles.inputError : {})
                }}
              />
              
              {/* BUTTON 1: SEARCH TEXT ADDRESS */}
              <button
                type="button"
                onClick={handleAddressSearch}
                disabled={locationStatus === 'loading'}
                style={{
                   ...styles.locationButton,
                   marginRight: '8px',
                   minWidth: '50px'
                }}
                title="Convert text to coordinates"
              >
                🔍
              </button>

              {/* BUTTON 2: GET BROWSER GPS */}
              <button
                type="button"
                onClick={handleGetLocation}
                disabled={locationStatus === 'loading'}
                style={{
                  ...styles.locationButton,
                  ...(locationStatus === 'success' ? styles.locationButtonSuccess : {}),
                  ...(locationStatus === 'loading' ? styles.locationButtonLoading : {})
                }}
                title="Use current GPS position"
              >
                {locationStatus === 'loading' ? '⏳' : '📍 GPS'}
              </button>
            </div>

            {validationErrors.location && (
              <span style={styles.errorText}>{validationErrors.location}</span>
            )}
            
            {/* Show coordinates if captured */}
            {formData.latitude && formData.longitude && (
              <div style={styles.coordsDisplay}>
                 ✓ Coordinates Locked: {formData.latitude.toFixed(5)}, {formData.longitude.toFixed(5)}
              </div>
            )}
          </div>

          {error && (
            <div style={styles.errorBanner}>
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            style={{
              ...styles.submitButton,
              ...(submitting ? styles.submitButtonDisabled : {})
            }}
          >
            {submitting ? 'SUBMITTING REPORT...' : '🚨 SUBMIT EMERGENCY REPORT'}
          </button>

          <div style={styles.disclaimer}>
            <span>ℹ️</span>
            <span>Your report will be prioritized based on severity and dispatched to the nearest rescue team.</span>
          </div>
        </form>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.85)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 3000,
    padding: '20px',
    overflow: 'auto',
  },
  container: {
    background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%)',
    border: '2px solid #1a3a4a',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '700px',
    maxHeight: '90vh',
    overflow: 'auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '24px 28px',
    borderBottom: '1px solid #1a3a4a',
    background: 'rgba(255, 23, 68, 0.1)',
  },
  headerContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  headerIcon: {
    fontSize: '36px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    color: '#ff1744',
    margin: 0,
    letterSpacing: '2px',
  },
  subtitle: {
    fontSize: '11px',
    color: '#8892b0',
    margin: 0,
    letterSpacing: '1px',
  },
  closeButton: {
    background: 'transparent',
    border: 'none',
    color: '#8892b0',
    fontSize: '24px',
    cursor: 'pointer',
    padding: '8px',
  },
  alertBanner: {
    background: 'rgba(255, 145, 0, 0.1)',
    border: '1px solid #ff9100',
    borderLeft: '4px solid #ff9100',
    padding: '12px 16px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '12px',
    color: '#ff9100',
  },
  form: {
    padding: '28px',
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginBottom: '20px',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    fontSize: '11px',
    fontWeight: 600,
    color: '#64ffda',
    letterSpacing: '1px',
    marginBottom: '8px',
  },
  required: {
    color: '#ff1744',
  },
  optional: {
    color: '#8892b0',
    fontWeight: 400,
  },
  input: {
    width: '100%',
    padding: '12px 14px',
    background: '#1a1a2e',
    border: '1px solid #1a3a4a',
    borderRadius: '6px',
    color: '#e6e6e6',
    fontSize: '14px',
    fontFamily: 'inherit',
    outline: 'none',
  },
  inputError: {
    borderColor: '#ff1744',
  },
  select: {
    width: '100%',
    padding: '12px 14px',
    background: '#1a1a2e',
    border: '1px solid #1a3a4a',
    borderRadius: '6px',
    color: '#e6e6e6',
    fontSize: '14px',
    fontFamily: 'inherit',
    cursor: 'pointer',
    outline: 'none',
  },
  textarea: {
    width: '100%',
    padding: '12px 14px',
    background: '#1a1a2e',
    border: '1px solid #1a3a4a',
    borderRadius: '6px',
    color: '#e6e6e6',
    fontSize: '14px',
    fontFamily: 'inherit',
    minHeight: '120px',
    resize: 'vertical',
    outline: 'none',
  },
  errorText: {
    display: 'block',
    fontSize: '11px',
    color: '#ff1744',
    marginTop: '6px',
  },
  charCount: {
    fontSize: '10px',
    color: '#8892b0',
    textAlign: 'right',
    marginTop: '4px',
  },
  locationGroup: {
    display: 'flex',
    gap: '8px',
  },
  locationButton: {
    padding: '12px 16px',
    background: 'rgba(0, 229, 255, 0.2)',
    border: '1px solid #00e5ff',
    borderRadius: '6px',
    color: '#00e5ff',
    fontSize: '12px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
    whiteSpace: 'nowrap',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  locationButtonSuccess: {
    background: 'rgba(105, 240, 174, 0.2)',
    borderColor: '#69f0ae',
    color: '#69f0ae',
  },
  locationButtonLoading: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
  coordsDisplay: {
    fontSize: '12px',
    color: '#69f0ae',
    marginTop: '6px',
    fontWeight: 600,
  },
  errorBanner: {
    background: 'rgba(255, 23, 68, 0.1)',
    border: '1px solid #ff1744',
    borderRadius: '6px',
    padding: '12px 16px',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    color: '#ff1744',
    fontSize: '13px',
  },
  submitButton: {
    width: '100%',
    padding: '16px',
    background: 'linear-gradient(135deg, #ff1744 0%, #d32f2f 100%)',
    border: '2px solid #ff1744',
    borderRadius: '8px',
    color: 'white',
    fontSize: '16px',
    fontWeight: 700,
    cursor: 'pointer',
    fontFamily: 'inherit',
    letterSpacing: '1px',
  },
  submitButtonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  disclaimer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginTop: '20px',
    padding: '12px',
    background: 'rgba(100, 255, 218, 0.05)',
    borderRadius: '6px',
    fontSize: '11px',
    color: '#8892b0',
    lineHeight: 1.5,
  },
};

export default EmergencyReportForm;