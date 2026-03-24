import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.greeting}>Welcome back, Employee</Text>
      
      {/* Budget Pool Usage Section */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Budget Pool Usage</Text>
        <Text style={styles.budgetAmount}>$2,500 / $10,000 HKD</Text>
        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { width: '25%' }]} />
        </View>
        <Text style={styles.budgetSub}>75% remaining for Q2 Travel</Text>
      </View>

      {/* Primary Actions */}
      <View style={styles.actionGrid}>
        <TouchableOpacity 
          style={styles.actionButton} 
          onPress={() => router.push('/scan')}
        >
          <MaterialIcons name="document-scanner" size={32} color="#6366f1" />
          <Text style={styles.actionText}>Scan/Upload{"\n"}Receipt</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton} 
          onPress={() => router.push('/past-uploads')}
        >
          <MaterialIcons name="history" size={32} color="#6366f1" />
          <Text style={styles.actionText}>Past Uploads{"\n"}& Status</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f3f4f6',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 20,
  },
  card: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 8,
  },
  budgetAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    marginBottom: 8,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#10b981', // green / success color
  },
  budgetSub: {
    fontSize: 12,
    color: '#6b7280',
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 15,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  actionText: {
    marginTop: 12,
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
    textAlign: 'center',
  }
});
