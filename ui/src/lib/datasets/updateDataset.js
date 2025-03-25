import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (dataset, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets/${dataset.id}`;
	const body = { ...dataset }
	console.log("hola", body)
	const { data, error } = await fetchEOTDL(url, token, 'PUT', body);
	if (error) throw new Error(error);
	return data;
};
