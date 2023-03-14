import { writable } from "svelte/store";
import ingestDataset from "$lib/datasets/ingestDataset";

const createDatasets = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    ingest: async (file, name, token) => {
      const data = await ingestDataset(file, name, token);
      update((current) => ({
        data: [...current.data, data],
      }));
    },
    // retrieve: async (project, token, features = true) => {
    //   set({ loading: true });
    //   try {
    //     const data = await retrieveAois(project, token, features);
    //     set({ loading: false, data });
    //   } catch (e) {
    //     console.error(e.message);
    //     set({ loading: false, error: e.message });
    //   }
    // },
    // remove: (id, token) => {
    //   deleteAoi(id, token);
    //   update((current) => ({
    //     ...current,
    //     data: current.data.filter((aoi) => aoi.id !== id),
    //   }));
    // },
    // download: (id, token) => {
    //   return downloadAoi(id, token);
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
