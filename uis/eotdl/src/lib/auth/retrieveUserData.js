import { EOTDL_API } from '$lib/env';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (token) => {
    let url = `${EOTDL_API}/auth/me`;
    const { data, error } = await fetchEOTDL(url, token);
    if (error) throw new Error(error);
	return data;
};