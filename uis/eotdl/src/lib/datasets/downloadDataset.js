import { EOTDL_API } from '$lib/env';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (id, token) => {
  let url = `${EOTDL_API}/datasets/${id}/download`;
  const { data, error } = await fetchEOTDL(url, token);
  if (error) throw new Error(error);
  return data;
};
