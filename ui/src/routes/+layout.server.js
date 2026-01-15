export async function load({ locals }) {
    const { user, id_token } = locals;
    if (user && id_token) {
        return {
            id_token,
            user
        };
    }
}

export const prerender = true;
