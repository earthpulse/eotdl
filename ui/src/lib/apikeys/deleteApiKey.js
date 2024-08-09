import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (token,keyId) => {
	let url = `${PUBLIC_EOTDL_API}/auth/keys/${keyId}`;
    const {data, error} = await fetchEOTDL(url,token, "DELETE");
    if (error) throw new Error(error);
	  return data;
};

