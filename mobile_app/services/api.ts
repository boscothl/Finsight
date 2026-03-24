import axios from 'axios';

// Replace with your local Django IP or Google Cloud Run URL later.
// Note: For Android Emulator, use 'http://10.0.2.2:8000/api'
// For iOS Simulator or physical device on the same wifi, use 'http://<YOUR_LOCAL_IP>:8000/api'
const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadReceipt = async (imageUri: string) => {
  try {
    const formData: any = new FormData();
    formData.append('receipt', {
      uri: imageUri,
      name: 'receipt.jpg',
      type: 'image/jpeg',
    });

    // Replace '/upload/' with your actual Django API route for receipt OCR
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error uploading receipt:', error);
    throw error;
  }
};

export default api;
