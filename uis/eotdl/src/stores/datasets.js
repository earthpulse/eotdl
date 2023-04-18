import { writable } from "svelte/store";
import ingestDataset from "../lib/datasets/ingestDataset";
import retrieveDatasets from "../lib/datasets/retrieveDatasets";
import downloadDataset from "../lib/datasets/downloadDataset";
import editDataset from "../lib/datasets/editDataset";
import likeDataset from "../lib/datasets/likeDataset";

const createDatasets = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    ingest: async (file, name, description, token) => {
      const data = await ingestDataset(file, name, description, token);
      update((current) => ({
        data: [...current.data, data],
      }));
    },
    retrieve: async (fetch, limit=null) => {
      set({ loading: true });
      try {
        const data = await retrieveDatasets(fetch, limit);
        set({ loading: false, data });
      } catch (e) {
        set({ loading: false, error: e.message });
      }
    },
    download: async (id, token) => {
      return downloadDataset(id, token);
    },
    edit: async (id, newName, newDescription, newTags, token) => {
      await editDataset(id, newName, newDescription, newTags, token);
      update((current) => ({
        data: current.data.map((dataset) =>
          dataset.id === id ? { ...dataset, name: newName, description: newDescription, tags: newTags } : dataset
        ),
      }));
    },
    like: async (id, token) => {
      likeDataset(id, token);
    }
  };
};

export const datasets = createDatasets();
