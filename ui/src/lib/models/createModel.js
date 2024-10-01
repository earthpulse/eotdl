import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (name, authors, source, license, token) => {
	const url = `${PUBLIC_EOTDL_API}/models`;
	const body = {name, authors, license, source};
	const { data, error } = await fetchEOTDL(url, token, 'POST', body);
	if (error) throw new Error(error);
	return data;
};
