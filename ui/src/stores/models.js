import { writable } from "svelte/store";
import retrieveModels from "$lib/models/retrieveModels";
import retrieveModel from "$lib/models/retrieveModel";
import likeModel from "$lib/models/likeModel";
import updateModel from "$lib/models/updateModel";
import createModel from "$lib/models/createModel";
import setModelVersion from "$lib/models/setModelVersion";
import ingestFile from "$lib/models/ingestFile";

const createModels = () => {
  const { subscribe, set, update } = writable({
    loading: false,
    error: null,
    data: [],
  });
  return {
    subscribe,
    retrieve: async (fetch, limit = null) => {
      set({ loading: true });
      try {
        const data = await retrieveModels(fetch, limit);
        set({ loading: false, data });
      } catch (e) {
        set({ loading: false, error: e.message });
      }
    },
    create: async (name, authors, source, license, token) => {
      const { model_id } = await createModel(name, authors, source, license, token);
      return model_id
    },
    ingest: async (model_id, file, token, version, name) => {
      await ingestFile(model_id, file, token, version);
      const data = await retrieveModel(name);
      update((current) => {
        const modelExists = current.data.find((model) => model.id === data.id)
        if (modelExists) {
          return {
            data: current.data.map((model) => model.id === data.id ? data : model)
          }
        }
        return {
          data: [data, ...current.data],
        }
      });
      return data
    },
    update: async (model, token) => {
      const data = await updateModel(model, token);
      update((current) => ({
        data: current.data.map((_model) =>
          _model.id === model.id ? data : _model
        ),
      }));
      return data;
    },
    like: async (id, token) => {
      likeModel(id, token);
    },
    setVersion: async (id, token) => {
      return await setModelVersion(id, token);
    },
  };
};

export const models = createModels();
