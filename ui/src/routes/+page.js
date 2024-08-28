import retrieveTags from '../lib/tags/retrieveTags'

export const load = async ({fetch}) => {
	const response = await fetch(`/api/posts`);
	const posts = await response.json();
	const tags = await retrieveTags(fetch)
	return {
		posts: posts.slice(0, 3),
		tags
	}
}

export const prerender = true;