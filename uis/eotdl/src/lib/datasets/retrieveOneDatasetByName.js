import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetcher from '$lib/shared/fetcher';

export default async (name, fetch) => {
  let url = `${PUBLIC_EOTDL_API}/datasets?name=${name}`;
  const { data, error } = await fetcher(url);
  if (error) throw new Error(error);
  return data;
};
