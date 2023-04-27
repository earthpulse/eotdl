export const load = async ({fetch}) => {
	const response = await fetch(`/api/posts`);
	const posts = await response.json();
	// console.log(posts);
	return {
		posts
	}
}

// export const prerender = true;
