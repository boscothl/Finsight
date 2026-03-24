import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      {/* Login Screen (First thing user sees) */}
      <Stack.Screen name="index" options={{ headerShown: false }} />
      
      {/* Main App Tabs */}
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      
      {/* Full Screen Modals / Stacks */}
      <Stack.Screen 
        name="scan" 
        options={{ title: 'Scan Receipt', presentation: 'fullScreenModal' }} 
      />
      <Stack.Screen 
        name="past-uploads" 
        options={{ title: 'Past Uploads' }} 
      />
      <Stack.Screen 
        name="edit-claim" 
        options={{ title: 'Edit Claim', presentation: 'modal' }} 
      />
    </Stack>
  );
}
