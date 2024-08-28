import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (dataset_id, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets/version/${dataset_id}`;
	const { data, error } = await fetchEOTDL(url, token, 'POST');
	if (error) throw new Error(error);
	return data;
};