import { sveltekit } from '@sveltejs/kit/vite';

const config = {
	plugins: [sveltekit()],
	test: {
	globals: true,
	environment: 'jsdom',
	},
};

export default config;
