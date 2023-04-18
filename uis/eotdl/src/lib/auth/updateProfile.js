import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (name, token) => {
    let url = `${PUBLIC_EOTDL_API}/auth`;
    const body = { name }
    const { data, error } = await fetchEOTDL(url, token, 'POST', body);
    if (error) throw new Error(error);
	return data;
};