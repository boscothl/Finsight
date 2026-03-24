import React, { useState } from 'react';
import { View, Text, StyleSheet, Button, Image, ActivityIndicator, TouchableOpacity, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';

export default function ScanScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<any>(null);

  const takePhoto = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    
    if (permissionResult.granted === false) {
      alert("Camera permission is required to scan receipts.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      handleUpload(result.assets[0].uri);
    }
  };

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      handleUpload(result.assets[0].uri);
    }
  };

  const handleUpload = (uri?: string) => {
    setLoading(true);
    setOcrResult(null);
    
    // Simulate Document AI OCR Delay
    setTimeout(() => {
      setOcrResult({ 
        merchant: "XYZ Tech Supplies", 
        amount: "1,250.00", 
        date: "2026-03-24",
        category: "Equipment"
      });
      setLoading(false);
    }, 2500);
  };

  const submitClaim = () => {
    // API logic will go here
    alert('Claim submitted successfully!');
    router.replace('/(tabs)/home');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.instructions}>
        Capture a clear photo of your receipt for automatic data extraction.
      </Text>

      <View style={styles.actionGrid}>
        <TouchableOpacity style={styles.actionBtn} onPress={takePhoto}>
          <MaterialIcons name="camera-alt" size={40} color="#6366f1" />
          <Text style={styles.btnText}>Open Camera</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionBtn} onPress={pickImage}>
          <MaterialIcons name="photo-library" size={40} color="#6366f1" />
          <Text style={styles.btnText}>Upload from Gallery</Text>
        </TouchableOpacity>
      </View>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.imagePreview} />
        </View>
      )}

      {loading && (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color="#6366f1" />
          <Text style={styles.loadingText}>Extracting receipt data with AI...</Text>
        </View>
      )}

      {ocrResult && !loading && (
        <View style={styles.resultCard}>
          <View style={styles.resultHeader}>
            <MaterialIcons name="check-circle" size={24} color="#10b981" />
            <Text style={styles.resultTitle}>Extraction Complete</Text>
          </View>
          
          <View style={styles.fieldRow}>
            <Text style={styles.fieldLabel}>Merchant</Text>
            <Text style={styles.fieldValue}>{ocrResult.merchant}</Text>
          </View>
          <View style={styles.fieldRow}>
            <Text style={styles.fieldLabel}>Amount (HKD)</Text>
            <Text style={styles.fieldValue}>${ocrResult.amount}</Text>
          </View>
          <View style={styles.fieldRow}>
            <Text style={styles.fieldLabel}>Date</Text>
            <Text style={styles.fieldValue}>{ocrResult.date}</Text>
          </View>

          <TouchableOpacity style={styles.submitBtn} onPress={submitClaim}>
            <Text style={styles.submitBtnText}>Confirm & Submit Claim</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  content: {
    padding: 20,
    alignItems: 'center',
  },
  instructions: {
    fontSize: 16,
    color: '#4b5563',
    textAlign: 'center',
    marginBottom: 24,
  },
  actionGrid: {
    flexDirection: 'row',
    gap: 15,
    width: '100%',
    marginBottom: 30,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  btnText: {
    marginTop: 10,
    fontWeight: '600',
    color: '#1f2937',
  },
  imageContainer: {
    width: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 10,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  imagePreview: {
    width: '100%',
    height: 300,
    resizeMode: 'contain',
    borderRadius: 8,
  },
  loadingBox: {
    alignItems: 'center',
    marginTop: 20,
  },
  loadingText: {
    marginTop: 12,
    color: '#4b5563',
    fontWeight: '500',
  },
  resultCard: {
    width: '100%',
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    borderBottomWidth: 1,
    borderColor: '#e5e7eb',
    paddingBottom: 15,
    gap: 8,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1f2937',
  },
  fieldRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  fieldLabel: {
    color: '#6b7280',
    fontSize: 15,
  },
  fieldValue: {
    color: '#1f2937',
    fontSize: 15,
    fontWeight: '600',
  },
  submitBtn: {
    backgroundColor: '#6366f1',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  submitBtnText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  }
});
