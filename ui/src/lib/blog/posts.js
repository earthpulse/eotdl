import fs from 'fs';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import readingTime from 'reading-time';
import matter from 'gray-matter';
import { Marked } from 'marked';
import { markedHighlight } from 'marked-highlight';
import prism from 'prismjs';
import loadLanguages from 'prismjs/components/index.js';
loadLanguages(['python', 'bash']);
import { parseEquations, parseInlieEquation } from './latex.js';

export const fetchPost = async (post) => {
	// read markdown file as string
	const fileContents = fs.readFileSync(`src/routes/blog/${post}`, 'utf8');
	// get metadata
	const matterResult = matter(fileContents);
	const readingStats = readingTime(matterResult.content);
	const printReadingTime = Math.ceil(readingStats.minutes);
	const printDate = format(new Date(matterResult.data.date), 'MMMM d, yyyy', {
		locale: es
	});
	// parse block latex equations before parsing the rest since marked will screw up the equations
	let content = await parseEquations(matterResult.content);
	// add target blank to links
	const marked = new Marked(
		markedHighlight({
			highlight(code, language, info) {
				// const language = hljs.getLanguage(language) ? language : 'plaintext';
				// return hljs.highlight(code, { language }).value;
				const highlightedCode = prism.highlight(
					code,
					prism.languages[language] || prism.languages.html,
					language
				);
				return `<pre class="language-${language}">${highlightedCode}</pre>`;
			}
		})
	);
	// open links in new tab
	const renderer = new marked.Renderer();
	renderer.link = function (href, title, text) {
		return `<a target="_blank" href="${href}">${text}</a>`;
	};
	marked.use({
		renderer,
		async: true,
		walkTokens: async (token) => {
			// parse inline equations
			if (token.type === 'text') token.text = await parseInlieEquation(token.text);
		}
	});
	content = await marked.parse(content);
	return {
		meta: {
			...matterResult.data,
			// tags: matterResult.data.tags?.split(',').map((tag) => tag.toLowerCase().trimStart()) || [],
			tags: matterResult.data.tags?.split(',').map((tag) => tag.trimStart()) || [],
			printReadingTime,
			printDate,
			path: `/blog/${post?.replace('.md', '')}`,
			slug: post?.replace('.md', '')
		},
		content
	};
};

export const fetchPostMetadata = async (post) => {
	const { meta } = await fetchPost(post);
	return meta;
};

export const fetchPosts = async () => {
	const files = fs.readdirSync('src/routes/blog');
	const posts = files.filter((file) => file.endsWith('.md'));
	const allPosts = await Promise.all(posts.map((post) => fetchPostMetadata(post)));
	return allPosts.sort((a, b) => {
		return new Date(b.date) - new Date(a.date);
	});
};
