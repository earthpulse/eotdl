import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (change_id, token) => {
    let url = `${PUBLIC_EOTDL_API}/changes/${change_id}`;
    const { data, error } = await fetchEOTDL(url, token);
    if (error) throw new Error(error);
    return data;
};
