export const load = async ({ fetch }) => {
	const response = await fetch(`/api/posts`);
	const posts = await response.json();
	const tags = posts
		.reduce((acc, post) => {
			post.tags.forEach((tag) => {
				if (!acc.includes(tag)) {
					acc.push(tag);
				}
			});
			return acc;
		}, [])
		.sort();
	return {
		posts,
		tags
	};
};

export const prerender = true;