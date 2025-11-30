// Psi MongoDB Initialization Script
// Creates collections and indexes for user preferences and time series data

// Switch to psi database
db = db.getSiblingDB('psi');

// User Preferences Collection
db.createCollection('user_preferences');
db.user_preferences.createIndex({ user_id: 1 }, { unique: true });

// Insert sample preference
db.user_preferences.insertOne({
    user_id: "sample-user-id",
    liked_foods: ["pizza", "pasta", "sushi"],
    disliked_foods: ["mushrooms"],
    dietary_restrictions: ["vegetarian"],
    notification_enabled: true,
    wellness_goals: ["reduce stress", "improve sleep"],
    created_at: new Date(),
    updated_at: new Date()
});

// Emotion Time Series Collection
db.createCollection('emotion_timeseries');
db.emotion_timeseries.createIndex({ user_id: 1, date: -1 });
db.emotion_timeseries.createIndex({ date: -1 });

// Insert sample time series data
db.emotion_timeseries.insertOne({
    user_id: "sample-user-id",
    date: new Date(),
    hourly_emotions: [
        { hour: 0, emotion: "sleep", score: 100 },
        { hour: 1, emotion: "sleep", score: 100 },
        { hour: 2, emotion: "sleep", score: 100 },
        { hour: 3, emotion: "sleep", score: 100 },
        { hour: 4, emotion: "sleep", score: 100 },
        { hour: 5, emotion: "sleep", score: 100 },
        { hour: 6, emotion: "sleep", score: 100 },
        { hour: 7, emotion: "calmness", score: 70 },
        { hour: 8, emotion: "focus", score: 80 },
        { hour: 9, emotion: "stress", score: 65 },
        { hour: 10, emotion: "stress", score: 75 },
        { hour: 11, emotion: "stress", score: 80 },
        { hour: 12, emotion: "calmness", score: 60 },
        { hour: 13, emotion: "happiness", score: 75 },
        { hour: 14, emotion: "focus", score: 85 },
        { hour: 15, emotion: "focus", score: 80 },
        { hour: 16, emotion: "fatigue", score: 70 },
        { hour: 17, emotion: "fatigue", score: 75 },
        { hour: 18, emotion: "happiness", score: 80 },
        { hour: 19, emotion: "calmness", score: 85 },
        { hour: 20, emotion: "calmness", score: 90 },
        { hour: 21, emotion: "calmness", score: 85 },
        { hour: 22, emotion: "sleep", score: 100 },
        { hour: 23, emotion: "sleep", score: 100 }
    ],
    wellness_score: 78,
    created_at: new Date()
});

// RLHF Training Data Collection
db.createCollection('rlhf_training_data');
db.rlhf_training_data.createIndex({ user_id: 1, timestamp: -1 });
db.rlhf_training_data.createIndex({ timestamp: -1 });

// Insert sample RLHF data
db.rlhf_training_data.insertOne({
    user_id: "sample-user-id",
    prompt: "Recommend food for stress",
    chosen_response: "Try magnesium-rich foods like dark chocolate and nuts",
    rejected_response: "Eat whatever you want",
    feedback_score: 5,
    timestamp: new Date()
});

// Recipe Cache Collection
db.createCollection('recipe_cache');
db.recipe_cache.createIndex({ ingredients_hash: 1 });
db.recipe_cache.createIndex({ created_at: 1 }, { expireAfterSeconds: 86400 }); // 24h TTL

// Food Detection Cache Collection
db.createCollection('food_detection_cache');
db.food_detection_cache.createIndex({ image_hash: 1 });
db.food_detection_cache.createIndex({ created_at: 1 }, { expireAfterSeconds: 86400 }); // 24h TTL

print("Psi MongoDB initialized successfully!");
print("Created collections:");
print("- user_preferences");
print("- emotion_timeseries");
print("- rlhf_training_data");
print("- recipe_cache");
print("- food_detection_cache");
