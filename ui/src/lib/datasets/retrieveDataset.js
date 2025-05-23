import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (name, id_token) => {
  let url = `${PUBLIC_EOTDL_API}/datasets?name=${name}`;
  const res = await fetch(url);
  const data = await res.json();
  if (res.status == 200)
    return data
  else if (res.status == 409 && id_token) {
    url = `${PUBLIC_EOTDL_API}/datasets/private?name=${name}`;
    const { data, error } = await fetchEOTDL(url, id_token);
    if (error) throw new Error(error);
    return data;
  }
  return null
};
