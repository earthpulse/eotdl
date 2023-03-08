import { AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET } from '$lib/env';
import pkg from 'jsonwebtoken';
const { decode, verify } = pkg;
import { JwksClient } from 'jwks-rsa';

let ISSUER = `https://${AUTH0_DOMAIN}`;
let JWKS_URL = `${ISSUER}/.well-known/jwks.json`;

async function privateDecodeTokenUncaught(idToken) {
  const decoded = decode(idToken, { complete: true });
  if (!decoded) return null;
  const { header } = decoded;
  if (!header) return null;

  const client = new JwksClient({ jwksUri: JWKS_URL });
  const key = await client.getSigningKey(header.kid);
  const signingKey = key.getPublicKey();
  const options = {
    issuer: `${ISSUER}/`,
    audience: AUTH0_CLIENT_ID,
    typ: 'JWT',
    complete: false
  };
  const payload = await verify(idToken, signingKey, options);
  return payload;
}

export async function retrieveToken(code, redirect_uri) {
  const tokens = await fetch(`${ISSUER}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      client_id: AUTH0_CLIENT_ID,
      client_secret: AUTH0_CLIENT_SECRET,
      code: code,
      redirect_uri
    })
  }).then((r) => r.json());
  return tokens;
}

export async function verifyToken(idToken) {
  let user = null;
  try {
    user = await privateDecodeTokenUncaught(idToken);
  } catch (error) {
    // if (error instanceof TokenExpiredError) {
    //   newIdToken = await callRefreshToken(refreshToken);
    //   try {
    //     const payload = await privateDecodeTokenUncaught(newIdToken);
    //     isOK = payload != null;
    //   } catch (error) {
    //     newIdToken = null;
    //     console.error('SEVERE ERROR while refreshing token');
    //     console.error(error);
    //   }
    // } else {
    console.error('Unhandled JsonWebToken error:');
    console.error(error);
    // }
  }
  return user;
}
