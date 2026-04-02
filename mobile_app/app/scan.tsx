import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, ActivityIndicator, TouchableOpacity, ScrollView, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { router, Stack } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { uploadReceipt, submitClaimData } from '../services/api';

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

  const handleUpload = async (uri?: string) => {
    if (!uri) {
      return;
    }

    setLoading(true);
    setOcrResult(null);

    try {
      const response = await uploadReceipt(uri);
      const extraction = response?.extraction || {};
      setOcrResult({
        merchant: extraction.merchant || '',
        amount: extraction.amount ? extraction.amount.toString() : '',
        date: extraction.date || '',
        category: extraction.category || '',
        note: '',
        public_url: extraction.public_url || '',
      });
    } catch {
      alert('Upload failed. Please ensure you are logged in and the API is reachable.');
    } finally {
      setLoading(false);
    }
  };

  const submitClaim = async () => {
    if (!ocrResult) return;
    try {
      setLoading(true);
      await submitClaimData({
        merchant: ocrResult.merchant,
        amount: parseFloat(ocrResult.amount) || 0,
        date: ocrResult.date || null,
        category: ocrResult.category,
        note: ocrResult.note,
        receipt_url: ocrResult.public_url,
      });
      alert('Claim submitted successfully!');
      router.replace('/(tabs)/home');
    } catch {
      alert('Failed to submit claim');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setOcrResult((prev: any) => ({ ...prev, [field]: value }));
  };

  return (
    <>
      <Stack.Screen 
        options={{
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ marginLeft: 16 }}>
              <MaterialIcons name="close" size={24} color="#000" />
            </TouchableOpacity>
          )
        }} 
      />
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
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{ width: '100%' }}>
          <View style={styles.resultCard}>
            <View style={styles.resultHeader}>
              <MaterialIcons name="check-circle" size={24} color="#10b981" />
              <Text style={styles.resultTitle}>Verify Extraction</Text>
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.fieldLabel}>Merchant</Text>
              <TextInput style={styles.inputField} value={ocrResult.merchant} onChangeText={(t) => updateField('merchant', t)} placeholder="Merchant Name" />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.fieldLabel}>Amount (HKD)</Text>
              <TextInput style={styles.inputField} value={ocrResult.amount} onChangeText={(t) => updateField('amount', t)} keyboardType="numeric" placeholder="0.00" />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.fieldLabel}>Date (YYYY-MM-DD)</Text>
              <TextInput style={styles.inputField} value={ocrResult.date} onChangeText={(t) => updateField('date', t)} placeholder="YYYY-MM-DD" />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.fieldLabel}>Category</Text>
              <TextInput style={styles.inputField} value={ocrResult.category} onChangeText={(t) => updateField('category', t)} placeholder="Category (e.g. Travel)" />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.fieldLabel}>Note</Text>
              <TextInput style={styles.inputField} value={ocrResult.note} onChangeText={(t) => updateField('note', t)} placeholder="Optional note" multiline />
            </View>

            <TouchableOpacity style={styles.submitBtn} onPress={submitClaim}>
              <Text style={styles.submitBtnText}>Confirm & Submit Claim</Text>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      )}
    </ScrollView>
    </>
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
  inputGroup: {
    marginBottom: 16,
  },
  fieldLabel: {
    color: '#4b5563',
    fontSize: 14,
    marginBottom: 6,
    fontWeight: '500',
  },
  inputField: {
    backgroundColor: '#f9fafb',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1f2937',
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
