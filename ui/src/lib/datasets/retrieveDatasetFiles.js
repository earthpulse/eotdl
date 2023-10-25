import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetch from '$lib/shared/fetcher';

export default async (id, version, token) => {
    let url = `${PUBLIC_EOTDL_API}/datasets/${id}/files?version=${version}`;
    const { data, error } = await fetch(url);
    if (error) throw new Error(error);
	return data;
};
