import { EOTDL_API } from '$lib/env';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (name, token) => {
    let url = `${EOTDL_API}/auth`;
    const body = { name }
    const { data, error } = await fetchEOTDL(url, token, 'POST', body);
    if (error) throw new Error(error);
	return data;
};