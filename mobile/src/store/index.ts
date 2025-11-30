/**
 * Redux Store Configuration
 */
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import foodReducer from './slices/foodSlice';
import wellnessReducer from './slices/wellnessSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    food: foodReducer,
    wellness: wellnessReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
