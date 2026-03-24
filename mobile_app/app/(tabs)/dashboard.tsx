import { View, Text, StyleSheet, Button } from 'react-native';
import { router } from 'expo-router';

export default function DashboardScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome back, Employee</Text>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Quick Actions</Text>
        <Button title="Scan New Receipt" onPress={() => router.push('/camera')} />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent Claims</Text>
        <Text>You have 2 pending claims.</Text>
        <Button title="View Claims" onPress={() => router.push('/claims')} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8f8f8',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    marginTop: 40,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  }
});