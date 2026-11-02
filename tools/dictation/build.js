/* 받아쓰기 중급반 · 겹받침 쓰기 연습 - 자료 만들기
   기초반(index.html)에 실린 성우 녹음 목록을 읽어, 쓰는 낱말의 소리 파일만 골라 넣는다.
   소리 파일 경로는 기초반과 같은 audio/aN.mp3 이므로 두 파일을 저장소 맨 위(index.html 옆)에 둔다.

   쓰기:  node build.js
   결과:  jung.html, gyeopbatchim.html, 녹음이-필요한-말.txt
*/
'use strict';
const fs = require('fs');
const path = require('path');

const SRC = process.argv[2] || 'idx.html';              // 기초반 index.html
const html = fs.readFileSync(SRC, 'utf8');
const AUDIO = JSON.parse(html.match(/window\.AUDIO = (\{[\s\S]*?\});/)[1]);
const WORDS = JSON.parse(html.match(/window\.WORDS_DATA = (\{[\s\S]*?\});/)[1]);

/* 소리 묶음(audio/audio.bin) 의 자리표.
   기초반에서 「소리 모두 받기」를 누르면 낱개 audio/aN.mp3 가 아니라 묶음 한 덩어리만
   저장됩니다. 그래서 비행기 모드에서 낱개 주소로 틀면 소리가 나지 않습니다.
   쓰는 파일의 자리(시작·길이)를 함께 넣어 두면, 중급반도 기초반처럼 묶음에서 잘라 씁니다.
   기초반이 묶음을 아직 안 만들었으면(window.AUDIO_BIN 없음) 예전처럼 낱개로 재생합니다. */
const BIN_SRC = (function () {
  const m = html.match(/window\.AUDIO_BIN = (\{[\s\S]*?\});/);
  return m ? JSON.parse(m[1]) : null;
})();

function binFor(paths) {
  if (!BIN_SRC || !BIN_SRC.lens) return null;
  const all = {};
  let at = 0;
  BIN_SRC.lens.forEach((len, i) => { all['audio/a' + i + '.mp3'] = [at, len]; at += len; });
  if (at !== BIN_SRC.total) {
    console.error('묶음 자리표가 맞지 않습니다: 조각 합 ' + at + ' ≠ total ' + BIN_SRC.total);
    process.exit(1);
  }
  const off = {}, lost = [];
  paths.filter(Boolean).forEach(p => { if (all[p]) off[p] = all[p]; else if (lost.indexOf(p) === -1) lost.push(p); });
  if (lost.length) {
    console.error('묶음에 없는 소리 파일: ' + lost.join(' '));
    process.exit(1);
  }
  return { file: BIN_SRC.file, total: BIN_SRC.total, off: off };
}

const missing = [];
function clip(word) {                                   // 낱말 → 소리 파일 (없으면 null)
  const f = AUDIO['w_' + word];
  if (!f && missing.indexOf(word) === -1) missing.push(word);
  return f || null;
}

/* ================= 낱말 받아쓰기 4단계 ================= */
const WORD_STAGES = [
  { id: 'w1', icon: '🌱', title: '받침 없는 낱말',
    tip: '받침이 없어 소리 나는 대로 쓰면 되는 낱말입니다.',
    words: ['모자','바지','치마','구두','우유','두부','사과','포도','배추','오이','고구마','커피',
            '시계','의자','베개','가위','도마','비누','지도','바다','나무','어머니','아버지','아기'] },
  { id: 'w2', icon: '🌿', title: '받침 있는 낱말',
    tip: '받침을 빠뜨리지 않도록 끝소리를 잘 들어 보세요.',
    words: ['김치','국수','된장','반찬','수건','안경','우산','가방','지갑','달력','냉장고','병원',
            '약국','감기','혈압','시장','통장','편지','택배','학교','경로당','정류장','아침','점심'] },
  { id: 'w3', icon: '🌾', title: '소리와 글자가 다른 낱말',
    tip: '들리는 소리와 쓰는 글자가 다릅니다. 부엌은 [부억]으로 들려도 「부엌」이라 씁니다.',
    words: ['부엌','무릎','그릇','젓가락','칫솔','옷장','빗자루','밥솥','속옷','곶감',
            '젓갈','이웃','버섯','씨앗','콧물','깻잎','좋다','놓다','높다','맛있다'] },
  { id: 'w4', icon: '🌳', title: '겹받침 낱말',
    tip: '받침이 두 개입니다. 소리는 하나만 나니 더 조심해서 써야 합니다.',
    words: ['값','흙','닭','앉다','읽다','많다','싫다','짧다','밝다','끓이다'] }
];

/* ================= 문장 받아쓰기 ================= */
const SENT1 = ['안녕하세요','고맙습니다','감사합니다','미안합니다','죄송합니다','반갑습니다',
               '축하합니다','괜찮습니다','여보세요','사랑합니다','잘했어요','맛있어요'];
const SENT2 = ['안녕히 가세요','안녕히 계세요','어서 오세요','잘 먹겠습니다','잘 먹었습니다',
               '안녕히 주무세요','또 봐요','처음 뵙겠습니다','새해 복 많이 받으세요','오래오래 사세요'];

/* 3단계 - 생활 문장. 어절마다 [바르게 쓴 말, 들려줄 낱말, 소리대로 잘못 쓴 말] */
const SENT3 = [
  [['오늘', null, null], ['병원에', '병원', '병워네'], ['갑니다', null, '감니다']],
  [['약을', '약', '야글'], ['아침에', '아침', '아치메'], ['먹습니다', '먹다', '먹씀니다']],
  [['시장에서', '시장', '시장에써'], ['김치를', '김치', null], ['샀습니다', '사다', '싿씀니다']],
  [['손자가', '손자', null], ['학교에', '학교', '학꾜에'], ['갔어요', '가다', '가써요']],
  [['오늘', null, null], ['날씨가', '날씨', null], ['참', null, null], ['좋습니다', '좋다', '조씀니다']],
  [['저녁에', '저녁', '저녀게'], ['국수를', '국수', '국쑤를'], ['먹었어요', '먹다', '머거써요']],
  [['우산을', '우산', '우사늘'], ['가지고', null, null], ['가세요', '가다', null]],
  [['통장에', '통장', null], ['돈을', '돈', '도늘'], ['넣었습니다', '놓다', '너어씀니다']],
  [['내일', '내일', null], ['경로당에', '경로당', '경노당에'], ['갑니다', null, '감니다']],
  [['안경을', '안경', '안경얼'], ['어디에', null, null], ['두었어요', null, '두어써요']],
  [['택배가', '택배', '택빼가'], ['경비실에', null, null], ['있어요', null, '이써요']],
  [['딸에게', '딸', null], ['편지를', '편지', null], ['씁니다', '쓰다', null]]
];

/* 3단계에서 통째로 들려줄 문장. 녹음 키는 d_<문장>, 말 속도는 문장이므로 -10%.
   목록을 tools/dictation/문장목록.json 으로 내보내고, tools/clips.py 가 그것을 읽습니다.
   그래서 소리를 만들 때 따로 적어 넣을 것이 없습니다:
     python tools/regen_audio_edge.py --missing
     python tools/build_audio_bundle.py
     python tools/stamp_sw.py
   이렇게 하면 문장도 다른 소리와 같이 묶음(audio/audio.bin)에 들어가므로
   비행기 모드에서도 소리가 납니다. */
const SENT3_TEXT = SENT3.map(s => s.map(p => p[0]).join(' '));
const SENT_KEY = s => 'd_' + s;

/* ================= 겹받침 쓰기 연습 ================= */
/* [겹받침, 이름, 소리 나는 쪽, 설명, 낱말들 [낱말, 읽기, 녹음낱말]] */
const GYEOP = [
  ['ㄱㅅ', 'ㄳ', 'ㄱ', '앞의 <b>ㄱ</b>이 소리 납니다.',
    [['넋', '넉', null], ['몫', '목', null]]],
  ['ㄴㅈ', 'ㄵ', 'ㄴ', '앞의 <b>ㄴ</b>이 소리 납니다.',
    [['앉다', '안따', '앉다'], ['얹다', '언따', null]]],
  ['ㄴㅎ', 'ㄶ', 'ㄴ', '앞의 <b>ㄴ</b>이 소리 나고, ㅎ은 뒷소리를 거세게 만듭니다.',
    [['많다', '만타', '많다'], ['괜찮다', '괜찬타', null], ['괜찮습니다', '괜찬씀니다', '괜찮습니다']]],
  ['ㄹㄱ', 'ㄺ', 'ㄱ', '뒤의 <b>ㄱ</b>이 소리 납니다.',
    [['닭', '닥', '닭'], ['흙', '흑', '흙'], ['읽다', '익따', '읽다'], ['밝다', '박따', '밝다']]],
  ['ㄹㅁ', 'ㄻ', 'ㅁ', '뒤의 <b>ㅁ</b>이 소리 납니다.',
    [['삶', '삼', null], ['젊다', '점따', null]]],
  ['ㄹㅂ', 'ㄼ', 'ㄹ', '앞의 <b>ㄹ</b>이 소리 납니다. 밟다만 [밥따]로 읽습니다.',
    [['짧다', '짤따', '짧다'], ['넓다', '널따', null], ['여덟', '여덜', null]]],
  ['ㄹㅅ', 'ㄽ', 'ㄹ', '앞의 <b>ㄹ</b>이 소리 납니다. 아주 드물게 씁니다.',
    [['외곬', '외골', null]]],
  ['ㄹㅌ', 'ㄾ', 'ㄹ', '앞의 <b>ㄹ</b>이 소리 납니다.',
    [['핥다', '할따', null], ['훑다', '훌따', null]]],
  ['ㄹㅍ', 'ㄿ', 'ㅂ', '뒤의 <b>ㅍ</b>이 ㅂ 소리로 납니다.',
    [['읊다', '읍따', null]]],
  ['ㄹㅎ', 'ㅀ', 'ㄹ', '앞의 <b>ㄹ</b>이 소리 나고, ㅎ은 뒷소리를 거세게 만듭니다.',
    [['싫다', '실타', '싫다'], ['끓이다', '끄리다', '끓이다'], ['옳다', '올타', null]]],
  ['ㅂㅅ', 'ㅄ', 'ㅂ', '앞의 <b>ㅂ</b>이 소리 납니다.',
    [['값', '갑', '값'], ['없다', '업따', null]]]
];

/* ================= 자료 묶기 ================= */
const used = {};
function put(w) { if (!w) return null; const f = clip(w); if (f) used[w] = f; return f; }

/* 받아쓰기이므로 「보이는 낱말」과 「들리는 녹음」이 달라서는 안 된다 */
const mismatch = [];
GYEOP.forEach(g => g[4].forEach(w => { if (w[2] && w[2] !== w[0]) mismatch.push(w[0] + ' → ' + w[2]); }));
DATA_WORD_CHECK: {
  WORD_STAGES.forEach(s => s.words.forEach(w => { if (!AUDIO['w_' + w]) mismatch.push(s.id + ' 단계의 ' + w + ' (녹음 없음)'); }));
}
if (mismatch.length) {
  console.error('보이는 말과 들리는 녹음이 다릅니다:\n  ' + mismatch.join('\n  '));
  process.exit(1);
}

WORD_STAGES.forEach(s => s.words.forEach(put));
SENT1.forEach(put);
SENT2.forEach(put);
SENT3.forEach(s => s.forEach(p => put(p[1])));
GYEOP.forEach(g => g[4].forEach(w => put(w[2])));

const FX = {
  praise: AUDIO['p_praise'] || null,
  wrong: AUDIO['p_wrong'] || null,
  perfect: AUDIO['g_perfect'] || null,
  good: AUDIO['g_good'] || null,
  ok: AUDIO['g_ok'] || null
};
const SC = [];
for (let i = 0; i <= 10; i++) SC.push(AUDIO['sc_' + i] || null);

/* 통문장 녹음이 들어온 것만 모은다. 없으면 지금처럼 낱말 소리로 문장을 만들어 봅니다. */
const SENT_AUDIO = {};
const sentMissing = [];
SENT3_TEXT.forEach(s => {
  const f = AUDIO[SENT_KEY(s)];
  if (f) SENT_AUDIO[s] = f; else sentMissing.push(s);
});

/* 두 화면이 쓰는 소리 파일 전부 — 묶음 자리표를 이 목록만큼만 넣는다 */
const USED_PATHS = Object.keys(used).map(k => used[k])
  .concat(Object.keys(SENT_AUDIO).map(k => SENT_AUDIO[k]))
  .concat(Object.keys(FX).map(k => FX[k]))
  .concat(SC);
const BIN = binFor(USED_PATHS);

const jungData = {
  A: used, FX: FX, SC: SC, BIN: BIN, SENT_AUDIO: SENT_AUDIO,
  W: WORD_STAGES,
  S1: SENT1, S2: SENT2, S3: SENT3
};
const gyeopData = { A: used, FX: FX, SC: SC, BIN: BIN, G: GYEOP };

/* 미리보기 판: 녹음을 파일 안에 통째로 넣어, 저장소에 올리지 않아도 소리가 납니다.
   소리 자체는 손대지 않습니다 - audio/ 의 mp3 를 그대로 담기만 합니다. */
function inlineAudio(data, links) {
  const map = {};
  /* 소리는 index.html 이 있는 곳(저장소 맨 위)의 audio/ 에서 가져옵니다.
     지금 폴더 기준으로 찾으면 tools/dictation 에서 돌릴 때 못 찾고
     소리 없는 미리보기가 조용히 만들어집니다. */
  const audioDir = path.join(path.dirname(path.resolve(SRC)), 'audio');
  function toData(p) {
    if (!p) return p;
    if (map[p]) return map[p];
    const file = path.join(audioDir, path.basename(p));
    if (!fs.existsSync(file)) {
      console.error('소리 파일을 못 찾았습니다: ' + file);
      return p;
    }
    map[p] = 'data:audio/mpeg;base64,' + fs.readFileSync(file).toString('base64');
    return map[p];
  }
  const out = JSON.parse(JSON.stringify(data));
  out.BIN = null;                                       // 미리보기는 소리가 파일 안에 있으므로 묶음을 안 씁니다
  Object.keys(out.A).forEach(k => { out.A[k] = toData(out.A[k]); });
  if (out.SENT_AUDIO) Object.keys(out.SENT_AUDIO).forEach(k => { out.SENT_AUDIO[k] = toData(out.SENT_AUDIO[k]); });
  Object.keys(out.FX).forEach(k => { out.FX[k] = toData(out.FX[k]); });
  out.SC = out.SC.map(toData);
  out.LINKS = links;
  return out;
}

function build(tpl, out, data, links) {
  let t = fs.readFileSync(tpl, 'utf8');
  if (t.indexOf('/*__DATA__*/') === -1) throw new Error(tpl + ' 에 /*__DATA__*/ 자리가 없습니다');
  t = t.replace('/*__DATA__*/', JSON.stringify(data));
  if (links) {
    Object.keys(links).forEach(from => {
      t = t.split('href="' + from + '"').join('href="' + links[from] + '"');
    });
  }
  fs.writeFileSync(out, t, 'utf8');
  console.log(out, (fs.statSync(out).size / 1024).toFixed(0) + 'KB');
}

build('jung.template.html', 'jung.html', jungData);
build('gyeopbatchim.template.html', 'gyeopbatchim.html', gyeopData);

/* node build.js idx.html --preview [겹받침 주소] [받아쓰기 주소] */
if (process.argv.indexOf('--preview') !== -1) {
  const i = process.argv.indexOf('--preview');
  const gbUrl = process.argv[i + 1] || 'gyeopbatchim.html';
  const jungUrl = process.argv[i + 2] || 'jung.html';
  const BASIC = 'https://jb9193.github.io/hangul/';
  build('jung.template.html', 'jung-preview.html', inlineAudio(jungData),
    { 'index.html': BASIC, 'gyeopbatchim.html': gbUrl });
  build('gyeopbatchim.template.html', 'gyeopbatchim-preview.html', inlineAudio(gyeopData),
    { 'index.html': BASIC, 'jung.html': jungUrl });
}

/* 소리 만드는 쪽(tools/clips.py)이 읽어 갈 문장 목록.
   이 파일이 있으면 regen_audio_edge.py 가 d_<문장> 키로 함께 만들어 줍니다. */
fs.writeFileSync('문장목록.json',
  JSON.stringify({ rate: '-10%', keyPrefix: 'd_', sentences: SENT3_TEXT }, null, 1) + '\n',
  'utf8');

/* 녹음이 아직 없는 말 - 기초반 만들 때 쓰신 성우 음성으로 뽑으시면 그대로 붙습니다 */
const needSent = sentMissing.slice();
const needWord = missing.slice();
const txt =
  '■ 아직 녹음이 없는 말\n' +
  '기초반과 같은 목소리(edge-tts ko-KR-SunHiNeural)로 아래를 만들면 그대로 붙습니다.\n' +
  '만드는 방법은 아래 ※ 를 보세요. 손으로 적어 넣을 것은 없습니다.\n\n' +
  '[낱말 ' + needWord.length + '개]\n' + (needWord.join('\n') || '(없음)') + '\n\n' +
  '[문장 ' + needSent.length + '개 - 3단계 생활 문장]\n' + (needSent.join('\n') || '(없음)') + '\n\n' +
  '※ 손으로 적어 넣을 것은 없습니다. 문장 목록은 문장목록.json 으로 나가 있고,\n' +
  '   tools/clips.py 가 그것을 읽어 d_<문장> 키로 소리를 만듭니다.\n' +
  '   인터넷이 되는 PC에서 이 세 줄이면 끝납니다.\n' +
  '     python tools/regen_audio_edge.py --missing\n' +
  '     python tools/build_audio_bundle.py\n' +
  '     python tools/stamp_sw.py\n' +
  '   그 뒤 build.js 를 다시 돌리면 3단계가 통문장 받아쓰기로 바뀝니다.\n' +
  '   (이미 있는 소리는 건드리지 않고, 없는 것만 더 만듭니다)\n' +
  '\n' +
  '■ 소리는 기초반과 똑같이 냅니다\n' +
  'jung.html · gyeopbatchim.html 은 기초반(index.html)의 재생 방식을 그대로 씁니다.\n' +
  '음색을 다듬거나 크기를 키우거나 빠르기를 바꾸지 않습니다.\n' +
  '같은 audio/ 파일을 같은 방법으로 틀기 때문에 기초반에서 듣던 목소리 그대로입니다.\n' +
  '\n' +
  '다만 audio/ 의 파일 자체가 32kbps · 24kHz 모노로 세게 눌려 있습니다.\n' +
  '(1,226개를 10MB에 담으려다 보니 그렇습니다)\n' +
  '기초반과 중급반이 같이 좋아지길 바라시면, 원본이 남아 있을 때 이렇게 다시 뽑으십시오.\n' +
  '  (1) 같은 용량으로 더 좋게 — AAC 48kbps (소리 크기 약 1.5배, 15MB 남짓)\n' +
  '      ffmpeg -i 원본.wav -ac 1 -ar 24000 -c:a aac -b:a 48k 결과.m4a\n' +
  '  (2) mp3 그대로 쓰시려면 64kbps 이상\n' +
  '      ffmpeg -i 원본.wav -ac 1 -ar 24000 -c:a libmp3lame -b:a 64k 결과.mp3\n' +
  '파일 이름(a0, a1 …)만 그대로 두시면 화면은 고칠 것이 없습니다.\n' +
  '기초반·중급반·겹받침 세 화면이 한꺼번에 좋아집니다.\n';
fs.writeFileSync('녹음이-필요한-말.txt', txt, 'utf8');
console.log('녹음이 필요한 낱말', needWord.length, '개 / 문장', needSent.length, '개');
console.log('통문장 받아쓰기  ' + Object.keys(SENT_AUDIO).length + ' / ' + SENT3_TEXT.length + ' 문장');
console.log(BIN
  ? '오프라인 소리  묶음 자리표 ' + Object.keys(BIN.off).length + '개 넣었습니다 (' + BIN.file + ')'
  : '오프라인 소리  기초반에 묶음(window.AUDIO_BIN)이 없어 낱개로 재생합니다');
