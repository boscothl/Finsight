import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { router } from 'expo-router';

// Status styling mapping to web standards
const statusStyles: any = {
  'Approved': { color: '#10b981', bg: '#d1fae5', icon: 'check-circle' },
  'Rejected': { color: '#ef4444', bg: '#fee2e2', icon: 'cancel' },
  'Pending': { color: '#6366f1', bg: '#e0e7ff', icon: 'hourglass-empty' },
  'Action Required': { color: '#f59e0b', bg: '#fef3c7', icon: 'error-outline' },
};

const mockClaims = [
  { id: '1', merchant: 'Cathay Pacific', amount: '120.00', date: '2026-03-24', status: 'Action Required', note: 'Missing receipt copy.' },
  { id: '2', merchant: 'AWS Services', amount: '250.00', date: '2026-03-20', status: 'Pending', note: '' },
  { id: '3', merchant: 'Starbucks', amount: '85.00', date: '2026-03-15', status: 'Approved', note: '' },
  { id: '4', merchant: 'Apple Store', amount: '12,500.00', date: '2026-03-10', status: 'Rejected', note: 'Exceeds equipment budget.' },
];

export default function PastUploadsScreen() {

  const handlePressClaim = (claim: any) => {
    if (claim.status === 'Action Required' || claim.status === 'Pending') {
      router.push({ pathname: '/edit-claim', params: { id: claim.id, merchant: claim.merchant, amount: claim.amount } });
    } else {
      // Maybe open a read-only modal or just show an alert for MVP
      alert(`Claim from ${claim.merchant} is ${claim.status}.`);
    }
  };

  const renderItem = ({ item }: { item: any }) => {
    const sStyle = statusStyles[item.status];
    
    return (
      <TouchableOpacity 
        style={styles.card} 
        onPress={() => handlePressClaim(item)}
        activeOpacity={0.7}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.merchant}>{item.merchant}</Text>
          <Text style={styles.amount}>${item.amount}</Text>
        </View>

        <Text style={styles.date}>{item.date}</Text>

        {item.note ? <Text style={styles.note}>Note: {item.note}</Text> : null}

        <View style={styles.footer}>
          <View style={[styles.badge, { backgroundColor: sStyle.bg }]}>
            <MaterialIcons name={sStyle.icon} size={14} color={sStyle.color} style={{ marginRight: 4 }} />
            <Text style={[styles.badgeText, { color: sStyle.color }]}>{item.status}</Text>
          </View>
          
          {(item.status === 'Action Required' || item.status === 'Pending') && (
            <MaterialIcons name="edit" size={20} color="#6b7280" />
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={mockClaims}
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
    gap: 16,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  merchant: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1f2937',
  },
  amount: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1f2937',
  },
  date: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 8,
  },
  note: {
    fontSize: 13,
    color: '#ef4444',
    fontStyle: 'italic',
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    borderTopWidth: 1,
    borderColor: '#f3f4f6',
    paddingTop: 12,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  }
});
