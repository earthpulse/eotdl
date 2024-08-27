import retrieveTags from '$lib/tags/retrieveTags';

export const load = async ({params, fetch}) => {
	const tags = await retrieveTags(fetch)
	return { tags, name: params.name };
}

export const ssr = false
export const prerender = false;