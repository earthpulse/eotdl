// src/routes/api/posts/+server.js
import { fetchPost } from '$lib/blog/posts';
import { json } from '@sveltejs/kit';

export const GET = async ({ params }) => {
	const post = await fetchPost(params.slug + '.md');
	return json(post);
};
