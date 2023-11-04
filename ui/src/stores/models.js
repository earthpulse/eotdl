import { writable } from "svelte/store";
import retrieveModels from "$lib/models/retrieveModels";
import likeModel from "$lib/models/likeModel";
import updateModel from "$lib/models/updateModel";


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
    update: async (model_id, name, content, authors, source, license, tags, token) => {
      const data = await updateModel(model_id, name, content, authors, source, license, tags, token);
      update((current) => ({
        data: current.data.map((model) => 
           model.id === model_id ? data : model          
        ),
      }));
      return data;
    },
    like: async (id, token) => {
      likeModel(id, token);
    },
  };
};

export const models = createModels();
