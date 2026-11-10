// k6 жүктемелік тест: дорама іздеу (NFR-01, NFR-02)
// Іске қосу (жеңіл):  k6 run -e SUPABASE_URL=https://XXXX.supabase.co -e ANON_KEY=... load/k6_search.js
// Толық (NFR-01, 200 VU) тек ЖЕКЕ ТЕСТ жобасында:  k6 run -e PROFILE=full ...
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = __ENV.SUPABASE_URL;
const KEY = __ENV.ANON_KEY;
const TABLE = __ENV.TABLE || 'doramas';      // кесте атын өз жобаңызға сәйкес өзгертіңіз
const COLUMN = __ENV.COLUMN || 'title';      // іздеу өрісі
const QUERIES = (__ENV.QUERIES || 'love,king,school,doctor,moon').split(',');

const smoke = [{ duration: '30s', target: 5 }, { duration: '30s', target: 0 }];
const full = [
  { duration: '2m', target: 50 },
  { duration: '3m', target: 200 },
  { duration: '2m', target: 0 },
];

export const options = {
  stages: __ENV.PROFILE === 'full' ? full : smoke,
  thresholds: {
    http_req_failed: ['rate<0.01'],          // қате үлесі < 1%
    http_req_duration: ['p(95)<1500'],       // NFR-02: p95 < 1.5 с
  },
};

export default function () {
  const q = QUERIES[Math.floor(Math.random() * QUERIES.length)];
  const url = `${BASE}/rest/v1/${TABLE}?select=*&${COLUMN}=ilike.*${q}*&limit=20`;
  const res = http.get(url, { headers: { apikey: KEY, Authorization: `Bearer ${KEY}` } });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
