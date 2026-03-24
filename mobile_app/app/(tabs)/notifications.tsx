import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

const mockNotifications = [
  { id: '1', title: 'Claim Approved', message: 'Your claim for "Uber/Taxi" ($120 HKD) was approved.', time: '2 hours ago', icon: 'check-circle', color: '#10b981' },
  { id: '2', title: 'Action Required', message: 'Admin requested receipt re-upload for "Lunch meeting".', time: '1 day ago', icon: 'error-outline', color: '#f59e0b' },
  { id: '3', title: 'Claim Rejected', message: 'Your claim for "Alcohol" ($500 HKD) violates policy.', time: '3 days ago', icon: 'cancel', color: '#ef4444' },
];

export default function NotificationsScreen() {
  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.notificationCard}>
      <View style={[styles.iconBox, { backgroundColor: item.color + '20' }]}>
        <MaterialIcons name={item.icon} size={28} color={item.color} />
      </View>
      <View style={styles.textContent}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.message}>{item.message}</Text>
        <Text style={styles.time}>{item.time}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={mockNotifications}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  listContent: {
    padding: 16,
    gap: 12,
  },
  notificationCard: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
    alignItems: 'center',
    gap: 16,
  },
  iconBox: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  textContent: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  message: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 6,
  },
  time: {
    fontSize: 12,
    color: '#9ca3af',
  }
});
