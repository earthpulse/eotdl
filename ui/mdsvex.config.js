import abbr from "remark-abbr"
import urls from "rehype-urls"
import slug from "rehype-slug"
import autoLinkHeadings from "rehype-autolink-headings"
import addClasses from "rehype-add-classes"

function processUrl(url, node) {
	if (node.tagName === "a") {
		node.properties.class = "text-link"
		if (!url.href.startsWith("/")) {
			// Open external links in new tab
			node.properties.target = "_blank"
			// Fix a security concern with offsite links
			// See: https://web.dev/external-anchors-use-rel-noopener/
			node.properties.rel = "noopener noreferrer"

		}
	}
}

const config = {
	extensions: ['.svx'],
	smartypants: {
		dashes: 'oldschool',
	},
	remarkPlugins: [abbr], // adds support for footnote-like abbreviations
	rehypePlugins: [
		// figure, // convert images into <figure> elements
		[urls, processUrl], // adds rel and target to <a> elements
		slug, // adds slug to <h1>-<h6> elements
		[autoLinkHeadings, { behavior: "wrap" }], // adds a <a> around slugged <h1>-<h6> elements
		[addClasses, { "ul,ol": "list" }] // add classes to these elements
	]
};

export default config;