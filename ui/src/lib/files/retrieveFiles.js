import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetch from '$lib/shared/fetcher';

export default async (collection, version) => {
    let url = `${PUBLIC_EOTDL_API}/stac/collections/${collection}/items?version=${version}`;
    const { data, error } = await fetch(url);
    if (error) throw new Error(error);
    return data.features;
};
