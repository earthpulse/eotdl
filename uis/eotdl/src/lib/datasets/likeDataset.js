import { EOTDL_API } from '$lib/env';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (id, token) => {
    let url = `${EOTDL_API}/datasets/${id}/like`;
    const { data, error } = await fetchEOTDL(url, token, 'POST');
    if (error) throw new Error(error);
	return data;
};
