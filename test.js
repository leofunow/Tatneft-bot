import http from 'k6/http';
import { sleep } from 'k6';
export const options = {
  vus: 20,
  duration: '60s',
  max_duration: '120s',
};
export default function () {
  http.get('http://localhost:8000/echo?message=What_is_russian_oil?');
  sleep(1);
}