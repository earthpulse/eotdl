import { writable } from "svelte/store";
import createDataset from "$lib/datasets/createDataset";
import ingestFile from "$lib/datasets/ingestFile";
import updateDataset from "$lib/datasets/updateDataset";
import retrieveDataset from "$lib/datasets/retrieveDataset";
import retrieveDatasets from "$lib/datasets/retrieveDatasets";
import downloadDataset from "$lib/datasets/downloadDataset";
import likeDataset from "$lib/datasets/likeDataset";
import retrieveDatasetFiles from "$lib/datasets/retrieveDatasetFiles";


const createDatasets = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    retrieveOne: async (name) => await retrieveDataset(name),
    create: async (name, authors, source, license, token) => {
      const { dataset_id } = await createDataset(name, authors, source, license, token);
      return dataset_id
    },
    ingest: async (dataset_id, file, token, name) => {
      await ingestFile(dataset_id, file, token);
      const data = await retrieveDataset(name);
      update((current) => {
        const datasetExists = current.data.find((dataset) => dataset.id === data.id)
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
    update: async (dataset_id, name, content, authors, source, license, tags, token) => {
      const data = await updateDataset(dataset_id, name, content, authors, source, license, tags, token);
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
    },
    retrieveFiles: async (id, version, token) => {
      return await retrieveDatasetFiles(id, version, token);
    }
  };
};

export const datasets = createDatasets();
