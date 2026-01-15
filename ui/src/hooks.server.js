import { handleLogto } from "@logto/sveltekit";
import {
  LOGTO_ENDPOINT,
  LOGTO_APP_ID,
  LOGTO_APP_SECRET,
  LOGTO_COOKIE_ENCRYPTION_KEY,
} from "$env/static/private";
import { PUBLIC_EOTDL_API } from "$env/static/public";
import { sequence } from "@sveltejs/kit/hooks";

const logtoHandler = handleLogto(
  {
    endpoint: LOGTO_ENDPOINT,
    appId: LOGTO_APP_ID,
    appSecret: LOGTO_APP_SECRET,
    scopes: ["email"],
  },
  {
    encryptionKey: LOGTO_COOKIE_ENCRYPTION_KEY,
  },
);

const persistUserHandler = async ({ event, resolve }) => {
  if (event.locals.user) {
    const token = await event.locals.logtoClient.getIdToken();
    event.locals.id_token = token;
    const response = await fetch(`${PUBLIC_EOTDL_API}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.ok) {
      event.locals.user = await response.json();
    }
  }
  return resolve(event);
};

export const handle = sequence(logtoHandler, persistUserHandler);
