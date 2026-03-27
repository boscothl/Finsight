import React, { useCallback, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, Dimensions, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { fetchHomeData, logout } from '../../services/api';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width - 64;

type BudgetPool = {
  id: number;
  name: string;
  group: string | null;
  total_budget_hkd: string;
  remaining_hkd: string;
  utilization_percentage: number;
};

type RecentClaim = {
  id: number;
  merchant: string | null;
  amount_hkd: string | null;
  status: string;
};

export default function HomeScreen() {
  const [pools, setPools] = useState<BudgetPool[]>([]);
  const [recentClaims, setRecentClaims] = useState<RecentClaim[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchHomeData();
      setPools(data?.pools || []);
      setRecentClaims(data?.recent_claims || []);
    } catch {
      setPools([]);
      setRecentClaims([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const renderPool = ({ item }: { item: BudgetPool }) => {
    const total = Number(item.total_budget_hkd || 0);
    const remaining = Number(item.remaining_hkd || 0);
    const spent = Math.max(total - remaining, 0);
    const usedPct = Math.max(0, Math.min(100, Number(item.utilization_percentage || 0)));

    return (
      <View style={[styles.card, { width: CARD_WIDTH }]}>
        <Text style={styles.cardTitle}>{item.name}</Text>
        <Text style={styles.cardSubtitle}>{item.group || 'General Budget Pool'}</Text>
        <Text style={styles.budgetAmount}>${spent.toFixed(2)} / ${total.toFixed(2)} HKD</Text>
        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { width: `${usedPct}%` }]} />
        </View>
        <Text style={styles.budgetSub}>{remaining.toFixed(2)} HKD remaining</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
          <View style={styles.header}>
      <Text style={styles.greeting}>Welcome back</Text>
      <TouchableOpacity onPress={async () => { await logout(); router.replace('/'); }} style={styles.logoutBtn}>
        <MaterialIcons name="logout" size={24} color="#ef4444" />
      </TouchableOpacity>
    </View>

      {loading ? (
        <View style={styles.loadingWrap}>
          <ActivityIndicator color="#6366f1" />
        </View>
      ) : pools.length > 0 ? (
                <FlatList
          data={pools}
          horizontal
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderPool}
          pagingEnabled
          decelerationRate="fast"
          snapToInterval={CARD_WIDTH + 12}
          snapToAlignment="start"
          showsHorizontalScrollIndicator={false}
          style={{ maxHeight: 200, flexGrow: 0, marginBottom: 20 }}
          contentContainerStyle={styles.carouselContent}
        />
      ) : (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Budget Pool Usage</Text>
          <Text style={styles.budgetSub}>No budget pools found for your account.</Text>
        </View>
      )}

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Recent Claims</Text>
        <Text style={styles.summaryText}>{recentClaims.length} recent claim(s) loaded</Text>
      </View>

      <View style={styles.actionGrid}>
        <TouchableOpacity 
          style={styles.actionBtn}
          onPress={() => router.push('/scan')}
        >
          <MaterialIcons name="receipt" size={32} color="#6366f1" />
          <Text style={styles.btnText}>Scan Receipt</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.actionBtn}
          onPress={() => router.push('/chatbot')}
        >
          <MaterialIcons name="chat" size={32} color="#6366f1" />
          <Text style={styles.btnText}>Ask Policy</Text>
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
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  logoutBtn: {
    padding: 8,
  },
  carouselContent: {
    paddingRight: 12,
    gap: 12,
    maxHeight: 200, 
    marginBottom: 20,
  },
  card: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
    maxHeight: 180,
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 8,
  },
  budgetAmount: {
    fontSize: 22,
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
    backgroundColor: '#10b981',
  },
  budgetSub: {
    fontSize: 12,
    color: '#6b7280',
  },
  summaryCard: {
    backgroundColor: '#ffffff',
    padding: 14,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1f2937',
  },
  summaryText: {
    marginTop: 4,
    color: '#6b7280',
  },
  loadingWrap: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    alignItems: 'center',
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionBtn: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    width: '48%',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  btnText: {
    marginTop: 10,
    fontSize: 14,
    fontWeight: '600',
    color: '#4b5563',
  },
});
