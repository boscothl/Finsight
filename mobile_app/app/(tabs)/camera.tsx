import { useState } from 'react';
import { View, Text, StyleSheet, Button, Image, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { uploadReceipt } from '../../services/api';

export default function CameraScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<any>(null);

  const takePhoto = async () => {
    // Ask for permissions
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    
    if (permissionResult.granted === false) {
      alert("You've refused to allow this app to access your camera!");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'], // Updated specifically to array form per recent expo versions
      allowsEditing: true,
      quality: 0.8, // Slightly compress to save time
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      handleUpload(result.assets[0].uri);
    }
  };

  const pickImage = async () => {
    // No permissions request is necessary for launching the image library
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], // Updated
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      handleUpload(result.assets[0].uri);
    }
  };

  const handleUpload = async (uri: string) => {
    setLoading(true);
    try {
      // Mock upload for now until backend is connected
      console.log('Uploading photo to backend...', uri);
      // const response = await uploadReceipt(uri);
      // setOcrResult(response);
      
      // Simulate backend delay (calling Cloud Run API)
      setTimeout(() => {
        setOcrResult({ merchant: "Demo Merchant", amount: "500 HKD", date: "2026-03-24" });
        setLoading(false);
      }, 2000);
      
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Scan Receipt</Text>
      
      <View style={styles.buttons}>
        <Button title="Take Photo" onPress={takePhoto} />
        <Button title="Pick from Gallery" onPress={pickImage} />
      </View>

      {image && <Image source={{ uri: image }} style={styles.image} />}
      
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
          <Text>Running Google Document AI...</Text>
        </View>
      )}

      {ocrResult && !loading && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Extracted Data (Review):</Text>
          <Text>Merchant: {ocrResult.merchant}</Text>
          <Text>Amount: {ocrResult.amount}</Text>
          <Text>Date: {ocrResult.date}</Text>
          <View style={{marginTop: 10}}>
             <Button title="Edit & Submit Claim" onPress={() => alert('Navigate to edit screen')} />
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    marginTop: 40,
  },
  buttons: {
    flexDirection: 'row',
    gap: 20,
    marginBottom: 20,
  },
  image: {
    width: 300,
    height: 300,
    resizeMode: 'contain',
    borderRadius: 8,
    marginBottom: 20,
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  resultContainer: {
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    width: '100%',
  },
  resultTitle: {
    fontWeight: 'bold',
    marginBottom: 10,
  }
});
