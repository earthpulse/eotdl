import retrieveDatasets from '../lib/datasets/retrieveDatasets'
import retrieveDatasetsLeaderboard from '../lib/datasets/retrieveDatasetsLeaderboard'
import retrievePopularDatasets from '../lib/datasets/retrievePopularDatasets'

export const load = async ({fetch}) => {
	const datasets = await retrieveDatasets(fetch, 3)
	const leaderboard = await retrieveDatasetsLeaderboard(fetch)
	const popular_datasets = await retrievePopularDatasets(fetch, 3)
	const response = await fetch(`/api/posts`);
	const posts = await response.json();
	return {
		leaderboard,
		datasets,
		popular_datasets,
		posts
	}
}