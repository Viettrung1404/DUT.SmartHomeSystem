import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  Text,
  Pressable,
  RefreshControl,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { SuggestionResponse, suggestionsAPI } from '@/services/api';

export default function SuggestionsScreen() {
  const colorScheme = useColorScheme();
  const [suggestions, setSuggestions] = useState<SuggestionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      const data = await suggestionsAPI.listMine(20, 0);
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSuggestions();
    setRefreshing(false);
  };

  const handleAcceptSuggestion = async (suggestionId: number, accept: boolean) => {
    try {
      await suggestionsAPI.accept(suggestionId, accept);
      setSuggestions(suggestions.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error('Failed to accept suggestion:', error);
    }
  };

  const getActionTypeColor = (type: string) => {
    switch (type) {
      case 'SCHEDULE':
        return '#4CAF50'; // Green
      case 'ALERT':
        return '#FF9800'; // Orange
      case 'AUTOMATION':
        return '#2196F3'; // Blue
      default:
        return '#9E9E9E'; // Gray
    }
  };

  const getActionTypeLabel = (type: string) => {
    switch (type) {
      case 'SCHEDULE':
        return 'Lịch biểu';
      case 'ALERT':
        return 'Cảnh báo';
      case 'AUTOMATION':
        return 'Tự động hóa';
      default:
        return type;
    }
  };

  if (loading) {
    return (
      <ThemedView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <ThemedText style={styles.loadingText}>Đang tải gợi ý...</ThemedText>
        </View>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={styles.scrollContent}
      >
        <View style={styles.header}>
          <ThemedText type="title">Gợi Ý Thông Minh</ThemedText>
          <ThemedText style={styles.subtitle}>
            Các gợi ý dựa trên thói quen sinh hoạt của bạn
          </ThemedText>
        </View>

        {suggestions.length === 0 ? (
          <View style={styles.emptyContainer}>
            <ThemedText style={styles.emptyText}>
              Chưa có gợi ý nào. Hãy tiếp tục sử dụng các thiết bị!
            </ThemedText>
          </View>
        ) : (
          suggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <View
                  style={[
                    styles.badge,
                    { backgroundColor: getActionTypeColor(suggestion.action_type) },
                  ]}
                >
                  <Text style={styles.badgeText}>
                    {getActionTypeLabel(suggestion.action_type)}
                  </Text>
                </View>
                <ThemedText style={styles.timestamp}>
                  {new Date(suggestion.created_at).toLocaleDateString('vi-VN')}
                </ThemedText>
              </View>

              <ThemedText type="defaultSemiBold" style={styles.cardTitle}>
                {suggestion.suggestion_json?.title || suggestion.suggestion_text.split(':')[0]}
              </ThemedText>

              <ThemedText style={styles.cardDescription}>
                {suggestion.suggestion_json?.description || suggestion.suggestion_text}
              </ThemedText>

              <View style={styles.actions}>
                <Pressable
                  style={[styles.button, styles.rejectButton]}
                  onPress={() => handleAcceptSuggestion(suggestion.id, false)}
                >
                  <ThemedText style={styles.buttonText}>Bỏ qua</ThemedText>
                </Pressable>

                <Pressable
                  style={[styles.button, styles.acceptButton]}
                  onPress={() => handleAcceptSuggestion(suggestion.id, true)}
                >
                  <ThemedText style={[styles.buttonText, styles.acceptButtonText]}>
                    Chấp nhận
                  </ThemedText>
                </Pressable>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
  },
  header: {
    marginBottom: 24,
  },
  subtitle: {
    marginTop: 8,
    fontSize: 14,
    opacity: 0.7,
  },
  emptyContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    textAlign: 'center',
    fontSize: 16,
    opacity: 0.6,
  },
  card: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    backgroundColor: '#f5f5f5',
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
  },
  badgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  timestamp: {
    fontSize: 12,
    opacity: 0.6,
  },
  cardTitle: {
    fontSize: 16,
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
    opacity: 0.8,
  },
  actions: {
    flexDirection: 'row',
    gap: 10,
  },
  button: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rejectButton: {
    backgroundColor: '#e0e0e0',
  },
  acceptButton: {
    backgroundColor: '#2196F3',
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  acceptButtonText: {
    color: 'white',
  },
});
