// import {datasets} from '$stores/datasets'
// import retrieveTags from '../../lib/tags/retrieveTags'
// import retrieveDatasetsLeaderboard from '../../lib/datasets/retrieveDatasetsLeaderboard'
// import retrieveLikedDatasets from '../../lib/datasets/retrieveLikedDatasets';

export const load = async ({fetch, parent}) => {
	const data = await parent()
	// await datasets.retrieve(fetch)
	const tags = [] //await retrieveTags(fetch)
	const leaderboard = [] //await retrieveDatasetsLeaderboard(fetch)
	let liked_datasets = []
	if (data.user)
		liked_datasets = [] //await retrieveLikedDatasets(fetch, data.id_token)
	return {
		tags,
		leaderboard,
		liked_datasets: liked_datasets.map(d => d.id)
	}
}