/**
 * Food Redux Slice
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface FoodState {
  history: any[];
  currentAnalysis: any | null;
  loading: boolean;
}

const initialState: FoodState = {
  history: [],
  currentAnalysis: null,
  loading: false,
};

const foodSlice = createSlice({
  name: 'food',
  initialState,
  reducers: {
    setHistory: (state, action: PayloadAction<any[]>) => {
      state.history = action.payload;
    },
    setCurrentAnalysis: (state, action: PayloadAction<any>) => {
      state.currentAnalysis = action.payload;
    },
    addToHistory: (state, action: PayloadAction<any>) => {
      state.history.unshift(action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setHistory, setCurrentAnalysis, addToHistory, setLoading } =
  foodSlice.actions;
export default foodSlice.reducer;
