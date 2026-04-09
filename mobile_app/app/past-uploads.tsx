import React, { useCallback, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import { fetchClaims } from '../services/api';

// Status styling mapping to web standards
const statusStyles: any = {
  'Approved': { color: '#10b981', bg: '#d1fae5', icon: 'check-circle' },
  'Rejected': { color: '#ef4444', bg: '#fee2e2', icon: 'cancel' },
  'Pending': { color: '#6366f1', bg: '#e0e7ff', icon: 'hourglass-empty' },
  'Action Required': { color: '#f59e0b', bg: '#fef3c7', icon: 'error-outline' },
};

type ClaimItem = {
  id: number;
  merchant: string | null;
  amount_hkd: string | null;
  date: string | null;
  status: string;
  category: string | null;
  note: string | null;
  receipts: Array<{ url: string | null }>;
  rejection_reason: string | null;
};

const toLabelStatus = (status: string) => {
  if (!status) return 'Pending';
  return status.charAt(0).toUpperCase() + status.slice(1);
};

export default function PastUploadsScreen() {
  const [claims, setClaims] = useState<ClaimItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadClaims = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchClaims();
      setClaims(Array.isArray(data) ? data : []);
    } catch {
      setClaims([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadClaims();
    }, [loadClaims])
  );

  const handlePressClaim = (claim: ClaimItem) => {
    const labelStatus = toLabelStatus(claim.status);
    const receiptUrl = claim.receipts && claim.receipts.length > 0 ? claim.receipts[0].url : '';
    router.push({ 
      pathname: '/claim-details', 
      params: { 
        id: claim.id, 
        merchant: claim.merchant || '', 
        amount: claim.amount_hkd || '0',
        date: claim.date || '',
        category: claim.category || '',
        note: claim.note || '',
        status: labelStatus,
        receiptUrl: receiptUrl || '',
        rejection_reason: claim.rejection_reason || ''
      } 
    });
  };

  const renderItem = ({ item }: { item: ClaimItem }) => {
    const labelStatus = toLabelStatus(item.status);
    const sStyle = statusStyles[labelStatus] || statusStyles.Pending;
    
    return (
      <TouchableOpacity 
        style={styles.card} 
        onPress={() => handlePressClaim(item)}
        activeOpacity={0.7}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.merchant}>{item.merchant || 'Unknown Merchant'}</Text>
          <Text style={styles.amount}>${item.amount_hkd || '0'}</Text>
        </View>

        <Text style={styles.date}>{item.date || '-'}</Text>

        {item.note ? <Text style={styles.note}>Note: {item.note}</Text> : null}

        <View style={styles.footer}>
          <View style={[styles.badge, { backgroundColor: sStyle.bg }]}>
            <MaterialIcons name={sStyle.icon} size={14} color={sStyle.color} style={{ marginRight: 4 }} />
            <Text style={[styles.badgeText, { color: sStyle.color }]}>{labelStatus}</Text>
          </View>
          
          {(labelStatus === 'Returned' || labelStatus === 'Pending') && (
            <MaterialIcons name="edit" size={20} color="#6b7280" />
          )}
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingWrap}>
        <ActivityIndicator color="#6366f1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={claims}
        keyExtractor={item => item.id.toString()}
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
  loadingWrap: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f3f4f6',
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
