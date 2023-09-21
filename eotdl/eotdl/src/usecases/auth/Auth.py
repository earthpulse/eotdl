from pydantic import BaseModel
import time 

from ...errors.auth import LoginError, AuthTimeOut

class Auth:
    def __init__(self, repo, api_repo, max_t=30, interval=2):
        self.repo = repo
        self.api_repo = api_repo
        self.max_t = max_t
        self.interval = interval

    class Inputs(BaseModel):
        pass 

    class Outputs(BaseModel):
        user: dict = None
        token: str = None

    def __call__(self, inputs: Inputs) -> Outputs:
        response = self.api_repo.login()
        if response.status_code != 200:
            raise LoginError()
        data = response.json()
        print('On your computer or mobile device navigate to: ', data['login_url'])
        authenticated = False
        t0 = time.time()
        while not authenticated and time.time() - t0 < self.max_t:
            response = self.api_repo.token(data['code'])
            token_data = response.json()
            if response.status_code == 200:
                print('Authenticated!')
                print('- Id Token: {}...'.format(token_data['id_token'][:10]))
                # save token data in file
                creds_path = self.repo.save_creds(token_data)
                print('Saved credentials to: ', creds_path)
                current_user = self.repo.decode_token(token_data)
                # TODO: call EOTDL api to retrieve services creds
                authenticated = True
                current_user['id_token'] = token_data['id_token']
                return self.Outputs(user=current_user)
            else:
                time.sleep(self.interval)
        if not authenticated:
            raise AuthTimeOut()