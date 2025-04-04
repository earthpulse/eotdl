import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (model, token) => {
	const url = `${PUBLIC_EOTDL_API}/models/${model.id}`;
	const body = { ...model }
	const { data, error } = await fetchEOTDL(url, token, 'PUT', body);
	if (error) throw new Error(error);
	return data;
};
