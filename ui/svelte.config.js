import { mdsvex } from 'mdsvex';
import adapter from '@sveltejs/adapter-vercel';
import mdsvexConfig from './mdsvex.config.js';
import path from "path";

const config = {
	kit: {
		adapter: adapter(),
		alias: {
			$stores: path.resolve("./src/stores"),
			$components: path.resolve("./src/components"),
			$styles: path.resolve("./src/styles"),
		}
	},
	preprocess: [mdsvex()],
	extensions: ['.svelte', ...mdsvexConfig.extensions],
};

export default config;
