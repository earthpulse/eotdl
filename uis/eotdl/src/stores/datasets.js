import { writable } from "svelte/store";
import ingestDataset from "../lib/datasets/ingestDataset";
import reuploadDataset from "../lib/datasets/reuploadDataset";
import retrieveDatasets from "../lib/datasets/retrieveDatasets";
import downloadDataset from "../lib/datasets/downloadDataset";
import likeDataset from "../lib/datasets/likeDataset";

const createDatasets = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    ingest: async (file, name, description, author, link, license, tags, token) => {
      const data = await ingestDataset(file, name,  author, link, license, description, tags, token);
      update((current) => ({
        data: [...current.data, data],
      }));
    },
    reupload: async (dataset_id, file, name, content, author, link, license, tags, token) => {
      const data = await reuploadDataset(dataset_id, file, name, content, author, link, license, tags, token);
      update((current) => ({
        data: current.data.map((dataset) => 
           dataset.id === dataset_id ? data : dataset          
        ),
      }));
      return data;
    },
    retrieve: async (fetch, limit=null) => {
      set({ loading: true });
      try {
        const data = await retrieveDatasets(fetch, limit);
        console.log(data)
        set({ loading: false, data });
      } catch (e) {
        set({ loading: false, error: e.message });
      }
    },
    download: async (id, token) => {
      return downloadDataset(id, token);
    },
    like: async (id, token) => {
      likeDataset(id, token);
    }
  };
};

export const datasets = createDatasets();
