import {datasets} from '$stores/datasets'
import retrieveTags from '$lib/tags/retrieveTags'

export const load = async ({fetch}) => {
	await datasets.retrieve(fetch)
	const tags = await retrieveTags(fetch)
	return {
		tags
	}
}