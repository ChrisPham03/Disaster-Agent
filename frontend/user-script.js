const form = document.getElementById('emergencyForm');
        const getLocationBtn = document.getElementById('getLocationBtn');
        const locationInput = document.getElementById('location');
        const locationError = document.getElementById('locationError');
        const successMessage = document.getElementById('successMessage');
        const submitBtn = document.getElementById('submitBtn');

        // Get user's location
        getLocationBtn.addEventListener('click', function() {
            if (!navigator.geolocation) {
                locationError.textContent = 'Geolocation is not supported by your browser';
                return;
            }

            getLocationBtn.disabled = true;
            getLocationBtn.textContent = 'Getting Location...';
            locationError.textContent = '';

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    locationInput.value = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
                    getLocationBtn.textContent = 'Location Captured ✓';
                    getLocationBtn.style.background = '#4caf50';
                },
                (error) => {
                    let errorMsg = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = 'Location access denied. Please enable location permissions.';
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
                    locationError.textContent = errorMsg;
                    getLocationBtn.disabled = false;
                    getLocationBtn.textContent = 'Get My Location';
                }
            );
        });

        // Handle form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Get form data
            const formData = {
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                emergencyType: document.getElementById('emergencyType').value,
                description: document.getElementById('description').value,
                location: document.getElementById('location').value,
                timestamp: new Date().toISOString()
            };

            // Log the data
            console.log('Emergency Report Submitted:', formData);

            // Show success message
            form.style.display = 'none';
            successMessage.style.display = 'block';

            
        });