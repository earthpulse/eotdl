function createAuth() {
    let user = $state(null);
    let id_token = $state(null);

    return {
        get user() {
            return user;
        },
        get id_token() {
            return id_token;
        },
        set user(newUser) {
            user = newUser;
        },
        set id_token(newIdToken) {
            id_token = newIdToken;
        }
    }
}

export default createAuth();