import mathjax from 'mathjax-node';

// for this to work in static generation mode need to be async
async function parseLatext(regex, text, _class, div) {
	return new Promise(async (resolve) => {
		const promises = [];
		// text.replace expects a function or string as second argument
		// in order to work with async we first need to replace all the matches with a promise
		// and then replace the matches with the results of the promises
		text.replace(regex, (match, id) => {
			const promise = new Promise((resolve2) =>
				mathjax.typeset({ math: match.replace(/\$/g, ''), svg: true }, (data) =>
					resolve2([id, data.svg])
				)
			);
			promises.push(promise);
			return promise;
		});
		const results = await Promise.all(promises);
		const replacements = results.reduce((acc, [id, v]) => {
			acc[id] = v?.replace(/<svg /, `<svg class="${_class}" `);
			// if (div) acc[id] = `<div style="overflow: scroll;">${acc[id]}</div>`;
			return acc;
		}, {});
		resolve(text.replace(regex, (match, id) => replacements[id]));
	});
}

export async function parseEquations(text) {
	return parseLatext(/\$\$(.*?)\$\$/gs, text, 'equation', true);
}

export async function parseInlieEquation(text) {
	return parseLatext(/\$(.*?)\$/gs, text, 'inline-equation', false);
}
