export const load = async ({ fetch, params }) => {
	const { slug } = params;
	const response = await fetch(`/api/posts/${slug}`);
	const post = await response.json();
	return {
		post,
		slug
	};
};

export const prerender = true;
