import { writable } from "svelte/store";
import ingestDataset from "$lib/datasets/ingestDataset";
import retrieveDatasets from "$lib/datasets/retrieveDatasets";
import downloadDataset from "$lib/datasets/downloadDataset";

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
    retrieve: async (fetch) => {
      set({ loading: true });
      try {
        const data = await retrieveDatasets(fetch);
        set({ loading: false, data });
      } catch (e) {
        set({ loading: false, error: e.message });
      }
    },
    download: async (id, token) => {
      return downloadDataset(id, token);
    },
        // remove: (id, token) => {
    //   deleteAoi(id, token);
    //   update((current) => ({
    //     ...current,
    //     data: current.data.filter((aoi) => aoi.id !== id),
    //   }));
    // },
    // edit: async (id, new_name, token) => {
    //   await editAoi(id, new_name, token);
    //   update((current) => ({
    //     data: current.data.map((aoi) =>
    //       aoi.id === id ? { ...aoi, name: new_name } : aoi
    //     ),
    //   }));
    // },
  };
};

export const datasets = createDatasets();
