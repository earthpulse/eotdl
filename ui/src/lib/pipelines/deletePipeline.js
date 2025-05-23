import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (pipelineId, id_token) => {
    let url = `${PUBLIC_EOTDL_API}/pipelines/deactivate/${pipelineId}`;
    const res = await fetchEOTDL(url, id_token, 'PATCH');
    const data = await res.json();
    if (res.status == 200)
        return data
    return null
};
