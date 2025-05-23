import { PUBLIC_EOTDL_API } from '$env/static/public';

export default async (fetch, limit = null) => {
  let url = `${PUBLIC_EOTDL_API}/pipelines`;
  if (limit) url += `?limit=${limit}`;
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (res.status == 200)
      return data
    throw new Error(data.message)
  } catch (err) {
    return []
  }
};
