/* extract_used.js — 앱이 실제로 소리 내어 읽는 말만 뽑아 tools/used.json 에 적는다.
 *
 *   node tools/extract_used.js hangul-go.html tools/used.json
 *
 * 읽지 않는 말(오답 보기 등)은 일부러 뺍니다. 음성을 만들어 봐야 쓰이지 않습니다.
 * 뽑는 규칙이 앱의 speak() 호출과 어긋나면 그 말만 기기 음성으로 새어 나가니,
 * 화면 쪽 문구를 고쳤으면 아래 UI 목록도 같이 고쳐 주세요.
 */
const fs = require('fs'), vm = require('vm');
const FILE = process.argv[2] || 'hangul-go.html';
const OUT = process.argv[3] || 'tools/used.json';

const html = fs.readFileSync(FILE, 'utf8');
const block = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1])
  .find(b => b.indexOf('const MODULES') >= 0);
if (!block) { console.error('hangul-go.html 에서 MODULES 를 찾지 못했습니다.'); process.exit(1); }

const ctx = { console };
vm.createContext(ctx);
vm.runInContext(block + ';globalThis.MM=MODULES;', ctx);
const M = ctx.MM;

const plain = s => String(s || '').replace(/<br\s*\/?>/gi, ' ').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
/* 앱의 sayKey() 와 똑같이 다듬어야 합니다. 끝의 ! ? . 은 떼어 같은 말로 봅니다. */
const key = s => plain(s).replace(/[!?.]+$/, '').trim();

const used = new Set();
const use = t => { const k = key(t); if (k) used.add(k); };

M.forEach(m => {
  (m.cards || []).forEach(c => {
    if (c.say) c.say.forEach(use);                 // 배우기 카드가 읽어 주는 말
    else if (c.doc) use(plain(c.doc.body));        // say 가 없으면 문서를 통째로 읽습니다
    else if (c.glyph) use(c.glyph);
    (c.ex || []).forEach(e => { (typeof e === 'string' ? [e] : [e[0], e[1]]).forEach(use); });
  });
  (m.quiz || []).forEach(q => {
    if (q.listen) use(q.listen);                   // 🔊 소리로 듣기
    use(plain(q.choices[q.answer]));               // 오답일 때 「정답은」 + 정답 보기
  });
  (m.orders || []).forEach(o => use(o.parts.join(' ')));   // 문장 차례 맞추기
  (m.sentences || []).forEach(x => use(x.text));           // 소리 내어 읽기
  (m.forms || []).forEach(f => {
    f.asks.forEach(a => use(plain(a.ask)));                // 서식 칸 찾기 물음
    f.rows.forEach(r => use('바른 칸은 ' + r + '입니다'));  // 그 풀이
  });
});

/* 화면이 늘 말하는 고정된 문구 — engine 의 speak() 인자와 글자까지 같아야 합니다 */
[
  '맞았습니다', '정답은', '딱 맞습니다', '차례가 조금 달랐습니다', '조각을 모두 눌러 문장을 채워 주세요',
  '모두 맞히셨습니다', '잘하셨습니다', '다시 한 번 해 보세요', '졸업을 축하드립니다', '한 번 더 해 보세요',
  '모두 잘 읽으셨습니다', '한 번 더 읽어 보세요', '아주 잘 읽으셨습니다', '잘 읽으셨습니다',
  '조금만 더 또박또박', '소리를 알아듣지 못했습니다. 다시 한 번 읽어 보세요'
].forEach(use);

fs.writeFileSync(OUT, JSON.stringify([...used], null, 1), 'utf8');
console.log('앱이 읽는 말 ' + used.size + '개를 ' + OUT + ' 에 적었습니다.');
