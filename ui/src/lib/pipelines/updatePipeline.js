import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (pipeline, token) => {
	const url = `${PUBLIC_EOTDL_API}/pipelines/${pipeline.id}`;
	const body = { ...pipeline }
	const { data, error } = await fetchEOTDL(url, token, 'PUT', body);
	if (error) throw new Error(error);
	return data;
};
