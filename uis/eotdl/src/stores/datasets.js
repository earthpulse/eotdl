import { writable } from "svelte/store";
import ingestFile from "../lib/datasets/ingestFile";
import updateDataset from "../lib/datasets/updateDataset";
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
    ingest: async (file, name, token) => {
      const data = await ingestFile(file, name, token);
      update((current) => {
        const datasetExists = current.data.find((dataset) => dataset.id === data.id)
        console.log(current)
        console.log(datasetExists)
        if (datasetExists) {
          return {
            data: current.data.map((dataset) => dataset.id === data.id ? data : dataset)
          }
        }
        return {
          data: [data, ...current.data],
        }
      });
      return data
    },
    update: async (dataset_id, name, content, author, link, license, tags, token) => {
      const data = await updateDataset(dataset_id, name, content, author, link, license, tags, token);
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
