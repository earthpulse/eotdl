import { EOTDL_API } from '$lib/env';

export default async (fetch) => {
	let url = `${EOTDL_API}/datasets`;
  const res = await fetch(url);
  const data = await res.json();
  if (res.status == 200) 
    return data
  throw new Error(data.detail);
};
