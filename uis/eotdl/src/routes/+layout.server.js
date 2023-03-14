export function load({locals}) {
    const {user, id_token} = locals;
    if (user) 
        return {
            user,
            id_token
        }
}

export const prerender = true;