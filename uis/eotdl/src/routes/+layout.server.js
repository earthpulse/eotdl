import retrieveUserData from '$lib/auth/retrieveUserData';

export async function load({locals, fetch}) {
    const {user, id_token} = locals;
    if (user) {
        const userData = await retrieveUserData(id_token, fetch)
        return {
            id_token,
            user: userData
        }
    }
}