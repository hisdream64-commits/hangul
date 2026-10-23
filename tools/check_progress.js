// check_progress.js — 진도 저장(⑦)을 브라우저로 자동 확인한다 (2026-10-23, 클라우드 세션에서 만듦).
//
//   준비: node 와 playwright (npm i -g playwright && npx playwright install chromium)
//   실행: python -m http.server 8765  (다른 창에서)
//         node tools/check_progress.js http://127.0.0.1:8765/
//   23항목이 모두 "ok" 이면 됩니다. 웹앱 자체에는 필요 없고, 고친 뒤 확인용입니다.
//   PW_CHROMIUM 환경변수에 크로미움 경로를 주면 그 브라우저를 씁니다.
//
// 진도 저장(⑦) 확인: 기초 학습을 넘기고 → 낱말 쪽을 넘기고 → 놀이를 한 판 끝낸 뒤
// 다시 열었을 때 같은 자리로 돌아오는지, 첫 화면에 "지난번"이 보이는지.
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8765/';
const fail = (m) => { console.log('FAIL ' + m); process.exitCode = 1; };
const ok = (c, m) => c ? console.log('ok   ' + m) : fail(m);

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined, args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 400, height: 800 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(BASE);
  ok(await page.$eval('#progBasics', e => e.textContent) === '', '처음에는 "지난번" 표시가 없다');
  ok(await page.$eval('#progBasics', e => getComputedStyle(e).display) === 'none', '빈 "지난번" 칸은 자리도 차지하지 않는다');

  // 기초 학습: 다음 ▶ 세 번 → ㄹ (4/14)
  await page.click('.menu-btn[data-go="basics"]');
  for (let i = 0; i < 3; i++) await page.click('#lvNext');
  ok((await page.$eval('#lvProgress', e => e.textContent)).startsWith('4 / 14'), '다음을 세 번 누르면 4/14');
  await page.click('#btnHome');
  await page.waitForTimeout(200);
  const pb = await page.$eval('#progBasics', e => e.textContent);
  ok(pb.includes('1단계 자음 4번째 글자'), '첫 화면에 "지난번: 1단계 자음 4번째 글자" — ' + pb);

  // 낱말: 두 번째 갈래, 2쪽
  await page.click('.menu-btn[data-go="words"]');
  const cat2 = await page.$$eval('#catRow .tab', ts => ts[1].textContent);
  await page.click('#catRow .tab:nth-child(2)');
  await page.click('#wpNext');
  ok((await page.$eval('#wpInfo', e => e.textContent)).startsWith('2 /'), '낱말 2쪽');
  await page.click('#btnHome');

  // 놀이: 10문제를 아무거나 눌러 끝낸다
  await page.click('.menu-btn[data-go="quiz"]');
  for (let i = 0; i < 10; i++) {
    await page.click('#qChoices .choice >> nth=0');
    await page.click('#qNext');
  }
  await page.waitForSelector('#quizResult', { state: 'visible' });
  ok((await page.$eval('#rBest', e => e.textContent)) === '', '첫 판에는 "가장 잘한 점수" 줄이 없다');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('hangul.progress')));
  ok(saved && saved.basics && saved.basics.step === 'ja' && saved.basics.idx === 3, '저장: 기초 ja/3 — ' + JSON.stringify(saved.basics));
  ok(saved.words && saved.words.cat === cat2 && saved.words.page === 1, '저장: 낱말 ' + cat2 + ' 2쪽');
  ok(saved.quiz && saved.quiz.n === 1 && typeof saved.quiz.last === 'number', '저장: 놀이 1번 — ' + JSON.stringify(saved.quiz));

  // 다시 연다 (새 탭: 세션 안 변수는 사라지고 localStorage 만 남는다)
  const page2 = await ctx.newPage();
  page2.on('pageerror', e => errors.push(String(e)));
  await page2.goto(BASE);
  ok((await page2.$eval('#progBasics', e => e.textContent)).includes('4번째 글자'), '다시 열어도 첫 화면 "지난번" 표시');
  ok((await page2.$eval('#progWords', e => e.textContent)).includes(cat2 + ' 2쪽'), '다시 열어도 낱말 "지난번" 표시');
  ok((await page2.$eval('#progQuiz', e => e.textContent)).includes('지난 점수'), '다시 열어도 놀이 점수 표시');
  ok((await page2.$eval('#lvProgress', e => e.textContent)).startsWith('4 / 14'), '기초 학습이 4/14 에서 이어진다 (소리 없이)');
  ok((await page2.$eval('#wpInfo', e => e.textContent)).startsWith('2 /'), '낱말이 2쪽에서 이어진다');
  ok(await page2.$eval('#catRow .tab:nth-child(2)', e => e.classList.contains('on')), '낱말 갈래 탭도 그 자리');

  // 기초 학습에 들어가면 안내(ui_resume)를 말한 뒤 글자를 보여 준다
  await page2.click('.menu-btn[data-go="basics"]');
  ok((await page2.$eval('#basicsHint', e => e.textContent)).includes('이어서'), '기초 학습 안내 글이 "이어서"로 바뀐다');
  ok((await page2.$eval('#lvGlyph', e => e.textContent)) === 'ㄹ', '보이는 글자는 ㄹ');
  // 3단계로 가서 자음을 고르면 그것도 저장된다
  await page2.click('[data-step="mix"]');
  await page2.click('#choRow .mini >> text=ㅁ');
  const s2 = await page2.evaluate(() => JSON.parse(localStorage.getItem('hangul.progress')).basics);
  ok(s2.step === 'mix' && s2.cho === 'ㅁ', '3단계·ㅁ 저장 — ' + JSON.stringify(s2));
  // 1단계 탭을 누르면 처음부터
  await page2.click('[data-step="ja"]');
  const s3 = await page2.evaluate(() => JSON.parse(localStorage.getItem('hangul.progress')).basics);
  ok(s3.step === 'ja' && s3.idx === 0, '1단계 탭 → 처음으로 저장');

  // 망가진 저장값이 있어도 앱이 열린다
  const page3 = await ctx.newPage();
  page3.on('pageerror', e => errors.push(String(e)));
  await page3.goto(BASE);
  await page3.evaluate(() => localStorage.setItem('hangul.progress', '{"basics":{"step":"zzz","idx":999,"cho":"X","bat":"Q","batIdx":-5},"words":{"cat":"없는갈래","page":77},"quiz":"bad"}'));
  await page3.reload();
  ok((await page3.$eval('#lvProgress', e => e.textContent)).startsWith('14 / 14'), '엉뚱한 값은 범위 안으로 — ' + await page3.$eval('#lvProgress', e => e.textContent));
  ok(await page3.$eval('#catRow .tab:nth-child(1)', e => e.classList.contains('on')), '없는 갈래면 첫 갈래');
  await page3.evaluate(() => localStorage.setItem('hangul.progress', 'not json'));
  await page3.reload();
  ok((await page3.$eval('#lvProgress', e => e.textContent)).startsWith('1 / 14'), 'JSON 이 아니어도 열린다');

  ok(errors.length === 0, '화면 오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
})().catch(e => { console.log('FAIL ' + e); process.exit(1); });
