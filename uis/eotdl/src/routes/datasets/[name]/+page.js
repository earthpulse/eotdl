import { PUBLIC_EOTDL_API } from '$env/static/public';
import retrieveTags from '$lib/tags/retrieveTags';

export const load = async ({params, fetch}) => {
	const url = `${PUBLIC_EOTDL_API}/datasets?name=${params.name}`;
	const res = await fetch(url)
	const dataset = await res.json();
	const tags = await retrieveTags(fetch)
	return { dataset, tags };
}

export const prerender = false;