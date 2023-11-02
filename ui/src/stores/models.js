import { writable } from "svelte/store";
import retrieveModels from "$lib/models/retrieveModels";
import likeModel from "$lib/models/likeModel";


const createModels = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    retrieve: async (fetch, limit=null) => {
      set({ loading: true });
      try {
        const data = await retrieveModels(fetch, limit);
        set({ loading: false, data });
      } catch (e) {
        set({ loading: false, error: e.message });
      }
    },
    like: async (id, token) => {
      likeModel(id, token);
    },
  };
};

export const models = createModels();
