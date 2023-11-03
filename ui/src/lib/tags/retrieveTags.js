import { PUBLIC_EOTDL_API } from '$env/static/public';

export default async (fetch) => {
	let url = `${PUBLIC_EOTDL_API}/tags`;
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (res.status == 200) 
      return data
    throw new Error(data.detail);
  } catch (err) {
    return []
  }

};
