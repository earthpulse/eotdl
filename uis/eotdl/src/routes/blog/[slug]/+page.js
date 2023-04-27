export const load = async ({ fetch, params }) => {
	const { slug } = params;
	const response = await fetch(`/api/post/${slug}`);
	const post = await response.json();
	return {
		post,
		slug
	};
};

export const prerender = true;
