import { EOTDL_API } from '$lib/env';
import fetcher from '$lib/shared/fetcher';

export default async (name, fetch) => {
  let url = `${EOTDL_API}/datasets?name=${name}`;
  const { data, error } = await fetcher(url);
  if (error) throw new Error(error);
  return data;
};
