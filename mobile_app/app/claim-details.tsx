import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView, Platform, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, router, Stack } from 'expo-router';

// Status styling mapping
const statusStyles: any = {
  'Approved': { color: '#10b981', bg: '#d1fae5' },
  'Rejected': { color: '#ef4444', bg: '#fee2e2' },
  'Pending': { color: '#6366f1', bg: '#e0e7ff' },
  'Action Required': { color: '#f59e0b', bg: '#fef3c7' },
};

export default function ClaimDetailsScreen() {
  const params = useLocalSearchParams();
  const labelStatus = params.status as string || 'Pending';
  const sStyle = statusStyles[labelStatus] || statusStyles.Pending;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      {/* Set Header Title */}
      <Stack.Screen options={{ title: 'Claim Details', headerBackTitle: 'Back' }} />
      
      <View style={styles.headerRow}>
        <Text style={styles.merchant}>{params.merchant || 'Unknown Merchant'}</Text>
        <View style={[styles.badge, { backgroundColor: sStyle.bg }]}>
           <Text style={[styles.badgeText, { color: sStyle.color }]}>{labelStatus}</Text>
        </View>
      </View>
      <Text style={styles.amount}>${params.amount || '0.00'} HKD</Text>
      
      {params.date ? <Text style={styles.detailText}>Date: {params.date}</Text> : null}
      {params.category ? <Text style={styles.detailText}>Category: {params.category}</Text> : null}
      
      {params.note ? (
        <View style={styles.noteBox}>
          <Text style={styles.noteLabel}>Note:</Text>
          <Text style={styles.noteText}>{params.note}</Text>
        </View>
      ) : null}

      {params.receiptUrl ? (
         <View style={styles.imageContainer}>
           <Text style={styles.imageLabel}>Attached Receipt:</Text>
           <Image
             source={{ uri: params.receiptUrl as string }}
             style={styles.receiptImage}
             resizeMode="contain"
           />
         </View>
      ) : (
         <Text style={styles.noImageText}>No receipt image attached.</Text>
      )}
      
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  merchant: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    flex: 1,
    marginRight: 10,
  },
  amount: {
    fontSize: 20,
    fontWeight: '600',
    color: '#6366f1',
    marginBottom: 16,
  },
  detailText: {
    fontSize: 16,
    color: '#4b5563',
    marginBottom: 8,
  },
  noteBox: {
    marginTop: 10,
    padding: 12,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    marginBottom: 20,
  },
  noteLabel: {
    fontWeight: '600',
    marginBottom: 4,
    color: '#374151',
  },
  noteText: {
    color: '#4b5563',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  imageContainer: {
    marginTop: 20,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
    alignItems: 'center',
  },
  imageLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#1f2937',
    alignSelf: 'flex-start',
  },
  receiptImage: {
    width: '100%',
    height: 400,
    borderRadius: 8,
    backgroundColor: '#e5e7eb',
  },
  noImageText: {
    marginTop: 20,
    fontStyle: 'italic',
    color: '#9ca3af',
  },
});
