import { sha1 } from 'js-sha1';

export default (file) => {
    return sha1(file)
}