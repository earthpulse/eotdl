import {datasets} from '$stores/datasets'

export const load = async ({fetch}) => {
	await datasets.retrieve(fetch)
	return {}
}