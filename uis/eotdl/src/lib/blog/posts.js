import fs from 'fs';
import { format } from 'date-fns';
import es from 'date-fns/locale/es/index.js';
import readingTime from 'reading-time';
import matter from 'gray-matter';
import { marked } from 'marked';
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
	const renderer = new marked.Renderer();
	renderer.link = function (href, title, text) {
		return `<a target="_blank" href="${href}">${text}</a>`;
	};
	// parse inline latex equations (acts only on paragraphs, not code or other blocks)
	// will screw up some of the symbols :(
	const walkTokens = async (token) => {
		if (token.type === 'text') token.text = await parseInlieEquation(token.text);
	};
	// parse markdown content with code highlighting
	marked.setOptions({
		highlight: function (code, language) {
			const highlightedCode = prism.highlight(
				code,
				prism.languages[language] || prism.languages.html,
				language
			);
			return `<pre class="language-${language}">${highlightedCode}</pre>`;
			// return highlightedCode;
		},
		renderer,
		async: true,
		walkTokens
	});
	// content = await marked.parse(content);
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
