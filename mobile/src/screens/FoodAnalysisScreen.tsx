/**
 * Mode 1: Food Analysis Screen
 * Real-time emotion-nutrition analysis
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { foodApi } from '../services/api';

export default function FoodAnalysisScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      analyzeFood(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      analyzeFood(result.assets[0].uri);
    }
  };

  const analyzeFood = async (imageUri: string) => {
    try {
      setLoading(true);

      // Create form data
      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'food.jpg',
      } as any);

      // Call API
      const response = await foodApi.uploadFood(formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing food:', error);
      alert('Failed to analyze food. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Food Analysis</Text>
        <Text style={styles.subtitle}>
          Upload a photo of your meal for nutrition analysis
        </Text>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.button} onPress={takePhoto}>
          <Text style={styles.buttonText}>Take Photo</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={pickImage}>
          <Text style={styles.buttonText}>Choose from Library</Text>
        </TouchableOpacity>
      </View>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.image} />
        </View>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6B4EFF" />
          <Text style={styles.loadingText}>Analyzing your food...</Text>
        </View>
      )}

      {result && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Analysis Results</Text>

          <View style={styles.caloriesCard}>
            <Text style={styles.caloriesValue}>
              {result.total_calories.toFixed(0)}
            </Text>
            <Text style={styles.caloriesLabel}>Calories</Text>
          </View>

          <View style={styles.foodItemsContainer}>
            <Text style={styles.sectionTitle}>Detected Foods</Text>
            {result.food_items.map((item: any, index: number) => (
              <View key={index} style={styles.foodItem}>
                <Text style={styles.foodName}>{item.name}</Text>
                <Text style={styles.foodDetails}>
                  {item.grams.toFixed(0)}g • {item.calories.toFixed(0)} cal
                </Text>
              </View>
            ))}
          </View>

          {result.emotion && (
            <View style={styles.emotionCard}>
              <Text style={styles.sectionTitle}>Your Emotion</Text>
              <Text style={styles.emotionType}>{result.emotion.type}</Text>
              <Text style={styles.emotionScore}>
                Confidence: {result.emotion.score}%
              </Text>
            </View>
          )}

          <View style={styles.recommendationCard}>
            <Text style={styles.sectionTitle}>Recommendation</Text>
            <Text style={styles.recommendationText}>
              {result.recommendation}
            </Text>
          </View>

          <View style={styles.xpCard}>
            <Text style={styles.xpText}>+{result.xp_gained} XP</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#6B4EFF',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  buttonContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  button: {
    flex: 1,
    backgroundColor: '#6B4EFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  imageContainer: {
    padding: 20,
    paddingTop: 0,
  },
  image: {
    width: '100%',
    height: 250,
    borderRadius: 12,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  resultContainer: {
    padding: 20,
    paddingTop: 0,
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  caloriesCard: {
    backgroundColor: '#6B4EFF',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  caloriesValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: 'white',
  },
  caloriesLabel: {
    fontSize: 18,
    color: 'white',
    opacity: 0.9,
  },
  foodItemsContainer: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  foodItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  foodName: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  foodDetails: {
    fontSize: 14,
    color: '#666',
  },
  emotionCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  emotionType: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6B4EFF',
    textTransform: 'capitalize',
  },
  emotionScore: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  recommendationCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  recommendationText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
  xpCard: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  xpText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
});
