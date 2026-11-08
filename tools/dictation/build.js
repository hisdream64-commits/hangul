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

/* ================= 3부 · 글 읽기 =================
   읽고 뜻을 알아보는 활동입니다. 1·2부는 듣고 쓰는 것이고, 여기는 읽는 것입니다.
   글에 쓰는 낱말은 모두 기초반 낱말 761개 안에서 골랐습니다. 중급에서 처음 보는
   낱말이 나오면 읽기가 아니라 낱말 공부가 되어 버립니다.
   (쓰지 않은 말: 하루·혼자·찍다·보내다·부치다 — 기초반에 없습니다)

   글 하나에 물음 셋. 한 단계는 글 셋이라 아홉 문제입니다.
   아홉으로 맞춘 까닭: 칭찬 소리(sc_0 … sc_10)가 열 문제까지뿐입니다.

   녹음 키는 r_<글 전체>. 글을 통째로 한 번에 읽어 줍니다.
   녹음이 없으면 🔊 를 내보내지 않습니다 — 읽기 활동이라 소리 없이도 됩니다. */
const READ_STAGES = [
  { id: 'r1', icon: '📖', title: '1단계 · 생활 이야기',
    tip: '글을 소리 내어 읽어 보신 뒤, 아래 물음에 답해 보세요. 글은 그대로 두고 찾아 읽으셔도 됩니다.',
    texts: [
      { lines: ['오늘 아침에 병원에 갔습니다.',
                '의사 선생님이 혈압이 높다고 하셨습니다.',
                '약을 받아서 아침과 저녁에 먹습니다.'],
        q: [['오늘 어디에 갔습니까?', ['병원', '약국', '시장'], 0],
            ['무엇이 높다고 하셨습니까?', ['혈압', '열', '값'], 0],
            ['약은 언제 먹습니까?', ['아침과 저녁', '점심에만', '저녁에만'], 0]] },
      { lines: ['어제 시장에 갔습니다.',
                '배추와 고추를 샀습니다.',
                '김치를 담그려고 삽니다.'],
        q: [['어제 어디에 갔습니까?', ['시장', '가게', '은행'], 0],
            ['무엇을 샀습니까?', ['배추와 고추', '감자와 무', '떡과 밥'], 0],
            ['무엇을 하려고 샀습니까?', ['김치를 담그려고', '국수를 먹으려고', '선물하려고'], 0]] },
      { lines: ['내일 경로당에 갑니다.',
                '친구들과 이야기하고 노래합니다.',
                '집에 있으면 심심합니다.'],
        q: [['내일 어디에 갑니까?', ['경로당', '공원', '병원'], 0],
            ['경로당에서 무엇을 합니까?', ['이야기하고 노래합니다', '밥을 먹습니다', '운동을 합니다'], 0],
            ['집에 있으면 어떻습니까?', ['심심합니다', '즐겁습니다', '따뜻합니다'], 0]] }
    ] },
  { id: 'r2', icon: '📗', title: '2단계 · 가족과 이웃',
    tip: '글을 읽고, 누가 무엇을 했는지 찾아보세요. 모르면 글을 한 번 더 읽어 보셔도 됩니다.',
    texts: [
      { lines: ['손자가 어제 전화를 했습니다.',
                '추석에 온다고 했습니다.',
                '떡을 사 놓고 기다립니다.'],
        q: [['누가 전화를 했습니까?', ['손자', '딸', '친구'], 0],
            ['언제 온다고 했습니까?', ['추석', '설날', '생일'], 0],
            ['무엇을 사 놓았습니까?', ['떡', '국수', '김치'], 0]] },
      { lines: ['오늘 날씨가 참 좋습니다.',
                '공원에 단풍이 많이 들었습니다.',
                '딸과 함께 걸었습니다.'],
        q: [['오늘 날씨가 어떻습니까?', ['참 좋습니다', '춥습니다', '비가 옵니다'], 0],
            ['공원에 무엇이 들었습니까?', ['단풍', '꽃', '눈'], 0],
            ['누구와 걸었습니까?', ['딸', '손자', '친구'], 0]] },
      { lines: ['어제 택배가 왔습니다.',
                '딸이 겨울 목도리를 주었습니다.',
                '전화해서 고맙다고 했습니다.'],
        q: [['어제 무엇이 왔습니까?', ['택배', '편지', '소포'], 0],
            ['딸이 무엇을 주었습니까?', ['겨울 목도리', '장갑', '모자'], 0],
            ['전화해서 무슨 말을 했습니까?', ['고맙다고', '미안하다고', '반갑다고'], 0]] }
    ] }
];
const READ_TEXTS = [];
READ_STAGES.forEach(s => s.texts.forEach(t => READ_TEXTS.push(t.lines.join(' '))));
const READ_KEY = t => 'r_' + t;

/* ================= 4부 · 내 이야기 쓰기 =================
   정답이 없는 활동입니다. 자기 생각과 겪은 일을 문장으로 써 보는 것이 목적이라
   맞고 틀림을 따지지 않습니다. 쓰신 글은 이 휴대폰 안에만 저장되고, 끝에 모아
   다시 읽어 드립니다.

   쓰는 길을 둘로 두었습니다 — 보기 낱말을 눌러 넣거나, 글자판으로 직접 쓰거나.
   글자판이 어려운 분도 낱말만 눌러 문장을 만드실 수 있습니다.
   보기 낱말은 모두 기초반 낱말 761개 안에서 골랐습니다
   (쓰지 않은 말: 고향·한글·글씨·책·노래 — 기초반에 없습니다).

   물음 녹음 키는 m_<물음>. 없으면 🔊 를 내보내지 않습니다. */
const WRITE_STAGES = [
  { id: 'm1', icon: '✏️', title: '1단계 · 오늘 하루 이야기',
    tip: '오늘 있었던 일을 한 문장으로 써 보세요. 정답은 없습니다. 보기 낱말을 눌러 넣으셔도 되고, 직접 쓰셔도 됩니다.',
    items: [
      { ask: '오늘 아침에 무엇을 드셨어요?', hint: '보기: 밥 · 국 · 김치 …',
        bank: ['밥', '국', '김치', '반찬', '된장', '국수', '떡', '우유', '커피', '먹다'] },
      { ask: '오늘 어디에 가셨어요?', hint: '안 나가셨으면 집이라고 쓰셔도 됩니다.',
        bank: ['집', '시장', '병원', '경로당', '공원', '가게', '은행', '가다'] },
      { ask: '오늘 날씨가 어땠어요?', hint: '',
        bank: ['좋다', '춥다', '덥다', '따뜻하다', '시원하다', '비', '눈', '바람', '날씨'] },
      { ask: '오늘 누구를 만나셨어요?', hint: '전화로 이야기한 분도 좋습니다.',
        bank: ['친구', '이웃', '딸', '아들', '손자', '손녀', '며느리', '만나다', '전화하다'] },
      { ask: '오늘 무엇을 하셨어요?', hint: '',
        bank: ['운동', '산책', '텔레비전', '라디오', '일하다', '쉬다', '요리하다', '보다'] },
      { ask: '오늘 기분이 어떠셨어요?', hint: '',
        bank: ['기쁘다', '즐겁다', '행복하다', '심심하다', '피곤하다', '고맙다', '반갑다'] }
    ] },
  { id: 'm2', icon: '📝', title: '2단계 · 나를 소개하기',
    tip: '나에 대해 한 문장씩 써 보세요. 쓰신 글은 이 휴대폰에 저장되어, 나중에 다시 읽어 보실 수 있습니다.',
    items: [
      { ask: '내가 좋아하는 음식은 무엇인가요?', hint: '',
        bank: ['김치', '국수', '떡', '된장', '나물', '고구마', '사과', '포도', '좋다'] },
      { ask: '내가 가고 싶은 곳은 어디인가요?', hint: '',
        bank: ['바다', '산', '강', '공원', '시장', '절', '교회', '여행', '가다'] },
      { ask: '내가 좋아하는 계절은 언제인가요?', hint: '왜 좋은지도 써 보세요.',
        bank: ['봄', '여름', '가을', '겨울', '꽃', '단풍', '따뜻하다', '시원하다'] },
      { ask: '우리 가족을 소개해 주세요.', hint: '',
        bank: ['남편', '아내', '아들', '딸', '손자', '손녀', '며느리', '사위', '가족'] },
      { ask: '요즘 배우고 싶은 것이 있으세요?', hint: '',
        bank: ['운동', '요리하다', '노래하다', '춤추다', '전화기', '사진', '읽다', '쓰다'] },
      { ask: '나에게 고마운 사람은 누구인가요?', hint: '',
        bank: ['어머니', '아버지', '남편', '아내', '딸', '아들', '친구', '이웃', '선생님', '고맙다'] }
    ] }
];
const WRITE_ASKS = [];
WRITE_STAGES.forEach(s => s.items.forEach(it => WRITE_ASKS.push(it.ask)));
const WRITE_KEY = a => 'm_' + a;

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
  // 소리 나는 쪽은 보기(ㄹ·ㅍ) 가운데 하나여야 「어느 쪽」 문제를 맞힐 수 있다. ㅍ 이 ㅂ 소리로 난다.
  ['ㄹㅍ', 'ㄿ', 'ㅍ', '뒤의 <b>ㅍ</b>이 ㅂ 소리로 납니다.',
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
// 「어느 쪽 소리가 날까요」의 정답(소리 나는 쪽)은 반드시 두 보기(겹받침의 앞·뒤 자음) 가운데 하나여야 한다
GYEOP.forEach(g => { if (g[0].indexOf(g[2]) === -1) { console.error('겹받침 ' + g[1] + ' 의 소리 나는 쪽 ' + g[2] + ' 이 보기(' + g[0][0] + '·' + g[0][1] + ')에 없습니다.'); process.exit(1); } });
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

/* 화면 안내 말 (메뉴 설명 읽어 주기). 기초반 index.html 의 window.UI_SAY 가 원본이고,
   tools/clips.py 가 ui_jung_* 로 녹음을 만듭니다.
   녹음이 아직 없는 말은 여기에 담기지 않으므로 🔊 단추도 나오지 않습니다 — 규칙 2.
   (안내 녹음이 없는데 단추만 내보내면 눌러도 아무 일이 없어 어르신이 고장인 줄 아십니다) */
const UI_KEYS = ['ui_jung_greet', 'ui_jung_w1', 'ui_jung_w2', 'ui_jung_w3', 'ui_jung_w4',
                 'ui_jung_s1', 'ui_jung_s2', 'ui_jung_s3', 'ui_jung_gb',
                 'ui_jung_r1', 'ui_jung_r2', 'ui_jung_m1', 'ui_jung_m2'];
/* 단계 「하는 방법」(ui_jung_tip_<단계>)과 틀린 이유(ui_jung_x_*) — 2026-11-08.
   화면에 보이는 글과 녹음 글이 글자 하나까지 같아야 한다(규칙 3). 다르면 일부러 실패한다. */
const TIP_IDS = ['w1', 'w2', 'w3', 'w4', 's1', 's2', 's3', 'r1', 'r2', 'm1', 'm2'];
const WHY_KEYS = ['ui_jung_x_cho', 'ui_jung_x_jung', 'ui_jung_x_jong', 'ui_jung_x_empty', 'ui_jung_x_nothing'];
const GUIDE_KEYS = TIP_IDS.map(id => 'ui_jung_tip_' + id).concat(WHY_KEYS);
UI_KEYS.push.apply(UI_KEYS, GUIDE_KEYS);
{
  const say = JSON.parse(html.match(/window\.UI_SAY = (\{[\s\S]*?\});<\/script>/)[1]);
  const shown = fs.readFileSync(__filename, 'utf8') + fs.readFileSync('jung.template.html', 'utf8');
  const bad = GUIDE_KEYS.filter(k => !say[k] || shown.indexOf("'" + say[k] + "'") === -1);
  if (bad.length) {
    console.error('안내 녹음 글이 화면 글과 다릅니다 (index.html UI_SAY ↔ 화면): ' + bad.join(', '));
    process.exit(1);
  }
}
const UI = {};
UI_KEYS.forEach(k => { if (AUDIO[k]) UI[k] = AUDIO[k]; });

/* 3부 글 읽기 — 글을 통째로 읽어 주는 녹음이 들어온 것만 모은다.
   없으면 🔊 를 내보내지 않는다. 읽기 활동이라 소리가 없어도 공부가 됩니다. */
const READ_AUDIO = {};
const readMissing = [];
READ_TEXTS.forEach(t => {
  const f = AUDIO[READ_KEY(t)];
  if (f) READ_AUDIO[t] = f; else readMissing.push(t);
});

/* 4부 내 이야기 쓰기 — 물음을 읽어 주는 녹음. 없으면 🔊 를 안 내보낸다. */
const WRITE_AUDIO = {};
const writeMissing = [];
WRITE_ASKS.forEach(a => {
  const f = AUDIO[WRITE_KEY(a)];
  if (f) WRITE_AUDIO[a] = f; else writeMissing.push(a);
});

/* 두 화면이 쓰는 소리 파일 전부 — 묶음 자리표를 이 목록만큼만 넣는다 */
const USED_PATHS = Object.keys(used).map(k => used[k])
  .concat(Object.keys(SENT_AUDIO).map(k => SENT_AUDIO[k]))
  .concat(Object.keys(FX).map(k => FX[k]))
  .concat(Object.keys(UI).map(k => UI[k]))
  .concat(Object.keys(READ_AUDIO).map(k => READ_AUDIO[k]))
  .concat(Object.keys(WRITE_AUDIO).map(k => WRITE_AUDIO[k]))
  .concat(SC);
const BIN = binFor(USED_PATHS);

const jungData = {
  A: used, FX: FX, SC: SC, BIN: BIN, SENT_AUDIO: SENT_AUDIO, UI: UI,
  W: WORD_STAGES,
  S1: SENT1, S2: SENT2, S3: SENT3,
  R: READ_STAGES, READ_AUDIO: READ_AUDIO,
  M: WRITE_STAGES, WRITE_AUDIO: WRITE_AUDIO
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
  /* 미리보기는 저장소 밖에서 혼자 열리므로, 상대경로 링크를 운영 주소로 바꿉니다. */
  const BASIC = 'https://urihangul.vercel.app/';
  const GO = 'https://urihangul.vercel.app/go/';
  build('jung.template.html', 'jung-preview.html', inlineAudio(jungData),
    { 'index.html': BASIC, 'go/': GO, 'gyeopbatchim.html': gbUrl });
  build('gyeopbatchim.template.html', 'gyeopbatchim-preview.html', inlineAudio(gyeopData),
    { 'index.html': BASIC, 'jung.html': jungUrl });
}

/* 소리 만드는 쪽(tools/clips.py)이 읽어 갈 문장 목록.
   이 파일이 있으면 regen_audio_edge.py 가 d_<문장> 키로 함께 만들어 줍니다. */
fs.writeFileSync('문장목록.json',
  JSON.stringify({
    rate: '-10%', keyPrefix: 'd_', sentences: SENT3_TEXT,
    /* 3부 글 읽기. 글 한 편을 통째로 한 조각으로 읽어 줍니다. */
    reading: { keyPrefix: 'r_', rate: '-10%', texts: READ_TEXTS },
    /* 4부 내 이야기 쓰기. 물음을 읽어 줍니다. */
    writing: { keyPrefix: 'm_', rate: '-10%', texts: WRITE_ASKS }
  }, null, 1) + '\n',
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
console.log('글 읽기 소리   ' + Object.keys(READ_AUDIO).length + ' / ' + READ_TEXTS.length + ' 편'
  + (readMissing.length ? '  (없어도 읽기는 됩니다 — 🔊 만 안 나옵니다)' : ''));
console.log('내 이야기 물음 ' + Object.keys(WRITE_AUDIO).length + ' / ' + WRITE_ASKS.length + ' 개'
  + (writeMissing.length ? '  (없어도 쓰기는 됩니다 — 🔊 만 안 나옵니다)' : ''));
console.log('메뉴 안내 🔊   ' + Object.keys(UI).length + ' / ' + UI_KEYS.length + ' 개'
  + (Object.keys(UI).length < UI_KEYS.length
     ? '  (없는 것은 단추를 안 내보냅니다 — PC에서 --missing)' : ''));
console.log(BIN
  ? '오프라인 소리  묶음 자리표 ' + Object.keys(BIN.off).length + '개 넣었습니다 (' + BIN.file + ')'
  : '오프라인 소리  기초반에 묶음(window.AUDIO_BIN)이 없어 낱개로 재생합니다');
