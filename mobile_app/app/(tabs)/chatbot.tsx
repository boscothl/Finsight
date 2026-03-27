import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, FlatList, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { sendComplianceQuestion } from '../../services/api';
import { ActivityIndicator } from 'react-native';

export default function ChatbotScreen() {
  const [messages, setMessages] = useState([
    { id: '1', text: 'Hello! I am the Finsight Compliance Bot. Ask me anything about our company budget policy or claim limits.', isBot: true }
  ]);
  const [inputText, setInputText] = useState('');

  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userText = inputText;
    const newMsg = { id: Date.now().toString(), text: userText, isBot: false };
    setMessages(prev => [...prev, newMsg]);
    setInputText('');
    setLoading(true);

    try {
      const result = await sendComplianceQuestion(userText);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: result.answer || "I'm sorry, I couldn't process that.",
        isBot: true
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: "Error contacting the server. Please try again later.",
        isBot: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }: { item: any }) => (
    <View style={[styles.messageBubble, item.isBot ? styles.botBubble : styles.userBubble]}>
      <Text style={[styles.messageText, item.isBot ? styles.botText : styles.userText]}>
        {item.text}
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
      />
      {loading && <ActivityIndicator style={{marginVertical: 10}} color="#6366f1" />}
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Ask a compliance question..."
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <TouchableOpacity style={styles.sendBtn} onPress={handleSend}>
          <MaterialIcons name="send" size={24} color="#ffffff" />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
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
  messageBubble: {
    maxWidth: '80%',
    padding: 14,
    borderRadius: 12,
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#ffffff',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 1,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#6366f1',
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  botText: {
    color: '#1f2937',
  },
  userText: {
    color: '#ffffff',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderColor: '#e5e7eb',
    alignItems: 'center',
    gap: 10,
  },
  input: {
    flex: 1,
    backgroundColor: '#f9fafb',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 10,
    fontSize: 15,
    maxHeight: 100,
  },
  sendBtn: {
    backgroundColor: '#6366f1',
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  }
});
