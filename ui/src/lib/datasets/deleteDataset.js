import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (datasetId, id_token) => {
    let url = `${PUBLIC_EOTDL_API}/datasets/${datasetId}/deactivate`;
    const res = await fetchEOTDL(url, id_token, 'PATCH');
    const data = await res.json();
    if (res.status == 200)
        return data
    return null
};
