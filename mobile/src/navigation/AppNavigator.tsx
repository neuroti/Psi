/**
 * Main App Navigator
 * Bottom tab navigation with 3 modes
 */
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Screens
import FoodAnalysisScreen from '../screens/FoodAnalysisScreen';
import FridgeRecipeScreen from '../screens/FridgeRecipeScreen';
import WellnessHubScreen from '../screens/WellnessHubScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'help-outline';

          if (route.name === 'FoodAnalysis') {
            iconName = focused ? 'restaurant' : 'restaurant-outline';
          } else if (route.name === 'FridgeRecipe') {
            iconName = focused ? 'nutrition' : 'nutrition-outline';
          } else if (route.name === 'WellnessHub') {
            iconName = focused ? 'heart' : 'heart-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6B4EFF',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="FoodAnalysis"
        component={FoodAnalysisScreen}
        options={{ title: 'Food' }}
      />
      <Tab.Screen
        name="FridgeRecipe"
        component={FridgeRecipeScreen}
        options={{ title: 'Recipes' }}
      />
      <Tab.Screen
        name="WellnessHub"
        component={WellnessHubScreen}
        options={{ title: 'Wellness' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}
