import { PUBLIC_EOTDL_API } from '$env/static/public';

export default async (name) => {
let url = `${PUBLIC_EOTDL_API}/models?name=${name}`;
  const res = await fetch(url);
  const data = await res.json();
  if (res.status == 200) 
    return data
  return null
};
