/**
 * Wellness Redux Slice
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface WellnessState {
  currentEmotion: any | null;
  wellnessScore: number;
  history: any[];
  loading: boolean;
}

const initialState: WellnessState = {
  currentEmotion: null,
  wellnessScore: 0,
  history: [],
  loading: false,
};

const wellnessSlice = createSlice({
  name: 'wellness',
  initialState,
  reducers: {
    setCurrentEmotion: (state, action: PayloadAction<any>) => {
      state.currentEmotion = action.payload;
    },
    setWellnessScore: (state, action: PayloadAction<number>) => {
      state.wellnessScore = action.payload;
    },
    setHistory: (state, action: PayloadAction<any[]>) => {
      state.history = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setCurrentEmotion, setWellnessScore, setHistory, setLoading } =
  wellnessSlice.actions;
export default wellnessSlice.reducer;
