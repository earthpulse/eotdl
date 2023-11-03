import { fetchPosts } from '$lib/blog/posts';
import { json } from '@sveltejs/kit';

export const GET = async () => {
	const allPosts = await fetchPosts();
	return json(allPosts);
};
