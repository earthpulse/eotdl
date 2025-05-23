import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (id_token) => {
    let url = `${PUBLIC_EOTDL_API}/datasets/private`;
    const { data, error } = await fetchEOTDL(url, id_token);
    if (error) throw new Error(error);
    return data;
};
