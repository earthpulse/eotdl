// import adapter from "@sveltejs/adapter-auto";
import preprocess from "svelte-preprocess";
import vercel from "@sveltejs/adapter-vercel";
import path from "path";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: preprocess({
    postcss: true,
  }),
  kit: {
    adapter: vercel(),
        alias: {
          $stores: path.resolve("./src/stores"),
          $components: path.resolve("./src/components"),
        },
  },
};

export default config;
