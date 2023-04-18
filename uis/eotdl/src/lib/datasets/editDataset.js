import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (id, name, description, tags, token) => {
    let url = `${PUBLIC_EOTDL_API}/datasets/${id}`;
    const body = {
        name,
        description,
        tags,
    }
    const { data, error } = await fetchEOTDL(url, token, 'POST', body);
    if (error) throw new Error(error);
	return data;
};
