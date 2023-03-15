import {datasets} from '$stores/datasets'
import retrieveTags from '$lib/tags/retrieveTags'
import retrieveDatasetsLeaderboard from '$lib/datasets/retrieveDatasetsLeaderboard'

export const load = async ({fetch}) => {
	await datasets.retrieve(fetch)
	const tags = await retrieveTags(fetch)
	const leaderboard = await retrieveDatasetsLeaderboard(fetch)
	return {
		tags,
		leaderboard
	}
}