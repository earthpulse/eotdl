import { PUBLIC_EOTDL_API } from '$env/static/public';
import retrieveTags from '$lib/tags/retrieveTags';

export const load = async ({params, fetch}) => {
	const url = `${PUBLIC_EOTDL_API}/models?name=${params.name}`;
	const res = await fetch(url)
	const model = await res.json();
	const tags = await retrieveTags(fetch)
	return { model, tags, name: params.name };
}

export const prerender = false;