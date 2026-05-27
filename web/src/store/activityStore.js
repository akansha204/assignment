import { create } from 'zustand';
import {
  fetchActivities as fetchAPI,
  approveActivity as approveAPI,
  rejectActivity as rejectAPI,
  editActivity as editAPI,
} from '../api/ingestion';

const useActivityStore = create((set) => ({
  activities: [],
  loading: false,
  error: null,

  fetchActivities: async () => {
    set({ loading: true, error: null });
    try {
      const res = await fetchAPI();
      set({ activities: res.data, loading: false });
    } catch (error) {
      set({ error, loading: false });
    }
  },

  approveActivity: async (id) => {
    set({ loading: true, error: null });
    try {
      await approveAPI(id);
      await useActivityStore.getState().fetchActivities();
    } catch (error) {
      set({ error, loading: false });
    }
  },

  rejectActivity: async (id) => {
    set({ loading: true, error: null });
    try {
      await rejectAPI(id);
      await useActivityStore.getState().fetchActivities();
    } catch (error) {
      set({ error, loading: false });
    }
  },

  editActivity: async (id, payload) => {
    set({ loading: true, error: null });
    try {
      await editAPI(id, payload);
      await useActivityStore.getState().fetchActivities();
    } catch (error) {
      set({ error, loading: false });
    }
  },
}));

export default useActivityStore;
