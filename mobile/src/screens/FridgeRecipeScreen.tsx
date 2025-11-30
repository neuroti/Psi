/**
 * Mode 2: Fridge Recipe Screen
 * Emotion-based recipe recommendations from fridge ingredients
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
  FlatList,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { fridgeApi } from '../services/api';

export default function FridgeRecipeScreen() {
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const pickImages = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,
      quality: 1,
    });

    if (!result.canceled) {
      const uris = result.assets.map((asset) => asset.uri);
      setImages(uris.slice(0, 5)); // Max 5 images

      if (uris.length > 0) {
        analyzeImagesAndGetRecipes(uris.slice(0, 5));
      }
    }
  };

  const analyzeImagesAndGetRecipes = async (imageUris: string[]) => {
    try {
      setLoading(true);

      // Create form data
      const formData = new FormData();
      imageUris.forEach((uri, index) => {
        formData.append('files', {
          uri,
          type: 'image/jpeg',
          name: `fridge_${index}.jpg`,
        } as any);
      });

      // Call API
      const response = await fridgeApi.detectIngredients(formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing fridge:', error);
      alert('Failed to analyze fridge. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderRecipe = ({ item }: { item: any }) => (
    <TouchableOpacity style={styles.recipeCard}>
      <Text style={styles.recipeName}>{item.name}</Text>
      <Text style={styles.recipeDetails}>
        {item.cooking_time} min • {item.difficulty}
      </Text>
      <Text style={styles.emotionMatch}>
        Emotion Match: {(item.emotion_score * 100).toFixed(0)}%
      </Text>
      <Text style={styles.ingredientMatch}>
        Available Ingredients: {item.available_ingredients}/{item.total_ingredients}
      </Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Fridge Recipes</Text>
        <Text style={styles.subtitle}>
          Upload photos of your fridge for personalized recipes
        </Text>
      </View>

      <TouchableOpacity style={styles.uploadButton} onPress={pickImages}>
        <Text style={styles.uploadButtonText}>
          Upload Fridge Photos (Max 5)
        </Text>
      </TouchableOpacity>

      {images.length > 0 && (
        <View style={styles.imagesContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {images.map((uri, index) => (
              <Image
                key={index}
                source={{ uri }}
                style={styles.fridgeImage}
              />
            ))}
          </ScrollView>
        </View>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6B4EFF" />
          <Text style={styles.loadingText}>Analyzing your fridge...</Text>
        </View>
      )}

      {result && (
        <View style={styles.resultContainer}>
          <View style={styles.ingredientsSection}>
            <Text style={styles.sectionTitle}>Detected Ingredients</Text>
            <View style={styles.ingredientsList}>
              {result.ingredients.map((ing: any, index: number) => (
                <View key={index} style={styles.ingredientChip}>
                  <Text style={styles.ingredientText}>{ing.name}</Text>
                </View>
              ))}
            </View>
          </View>

          <View style={styles.emotionSection}>
            <Text style={styles.sectionTitle}>Your Current Emotion</Text>
            <Text style={styles.emotionText}>{result.emotion_type}</Text>
          </View>

          <View style={styles.recipesSection}>
            <Text style={styles.sectionTitle}>
              Recommended Recipes ({result.recipes.length})
            </Text>
            <FlatList
              data={result.recipes}
              renderItem={renderRecipe}
              keyExtractor={(item, index) => index.toString()}
              scrollEnabled={false}
            />
          </View>

          {result.shopping_list.length > 0 && (
            <View style={styles.shoppingSection}>
              <Text style={styles.sectionTitle}>Shopping List</Text>
              {result.shopping_list.map((item: string, index: number) => (
                <Text key={index} style={styles.shoppingItem}>
                  • {item}
                </Text>
              ))}
            </View>
          )}
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
    backgroundColor: '#4CAF50',
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
  uploadButton: {
    margin: 20,
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  uploadButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  imagesContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  fridgeImage: {
    width: 120,
    height: 120,
    borderRadius: 8,
    marginRight: 12,
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
  ingredientsSection: {
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
  ingredientsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  ingredientChip: {
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
  },
  ingredientText: {
    color: '#4CAF50',
    fontSize: 14,
  },
  emotionSection: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  emotionText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    textTransform: 'capitalize',
  },
  recipesSection: {
    marginBottom: 16,
  },
  recipeCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  recipeName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  recipeDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  emotionMatch: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '500',
  },
  ingredientMatch: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  shoppingSection: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
  },
  shoppingItem: {
    fontSize: 16,
    paddingVertical: 8,
    color: '#333',
  },
});
