import retrieveUserData from '../lib/auth/retrieveUserData';


export async function load({ locals }) {
    const { user, id_token } = locals;
    const userData = await retrieveUserData(id_token, fetch)
    // console.log(userData);
    if (user && id_token) {
        return {
            id_token,
            user: userData
        };
    }
}

export const prerender = true;
