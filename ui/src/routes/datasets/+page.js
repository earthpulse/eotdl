import retrieveTags from '$lib/tags/retrieveTags'

export const load = async ({ fetch }) => {
	const tags = await retrieveTags(fetch)
	return {
		tags
	}
}

export const prerender = false;