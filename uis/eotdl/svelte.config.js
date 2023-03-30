// import adapter from "@sveltejs/adapter-auto";
import preprocess from "svelte-preprocess";
import vercel from "@sveltejs/adapter-vercel";
import path from "path";
import { mdsvex } from 'mdsvex'; 
import mdsvexConfig from './mdsvex.config.js'; 


/** @type {import('@sveltejs/kit').Config} */
const config = {
  extensions: ['.svelte', ...mdsvexConfig.extensions],
  preprocess: [
    preprocess({postcss: true }),
    mdsvex(mdsvexConfig)
  ],
  kit: {
    adapter: vercel(),
        alias: {
          $stores: path.resolve("./src/stores"),
          $components: path.resolve("./src/components"),
        },
  },
};

export default config;
