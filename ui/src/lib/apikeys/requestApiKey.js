import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (token) => {
	let url = `${PUBLIC_EOTDL_API}/auth/keys`;
    const {data, error} = await fetchEOTDL(url, token, "POST");
    if (error) throw new Error(error);
	return data;
};
