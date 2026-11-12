/* K-Rank Internationalization (i18n) Engine - Korean (ko) & English (en) */

const i18nDict = {
  ko: {
    title: "K-Rank (케이랭크) 🏆 - 글로벌 K-Pop 팩트 정량 랭킹 플랫폼",
    tagline: "100% 팩트 데이터 기반 글로벌 K-Pop 정량 랭킹",
    methodologyBtn: "📐 산출 공식",
    supportBtn: "☕ 개발자 후원",
    feedbackBtn: "✉️ 의견 보내기",
    searchPlaceholder: "아티스트, 소속사, 팬덤 검색...",
    top3Heading: "🏆 Global Top 3 Leaders",
    top3Subheading: "(Spotify, Circle Chart, YouTube 팩트 데이터 정량 산출)",
    seededCount: "50팀 아티스트 가동 중",
    gridTitleOverall: "🔥 K-Rank Overall Leaderboard",
    gridTitleMusic: "🎵 글로벌 음원 퀸/왕 Top Leaderboard",
    gridTitleAlbum: "💿 음반 초동 및 누적 제왕 Top Leaderboard",
    gridTitleYoutube: "📺 유튜브 MV 뷰왕 Top Leaderboard",
    gridTitleSns: "📲 소셜 파워 Top Leaderboard",
    gridTitleCheer: "💖 실시간 팬덤 화력 랭킹",
    gridTitleGen5: "🌟 5세대 대표 아티스트 랭킹",
    gridTitleGen4: "⚡ 4세대 대표 아티스트 랭킹",
    cardInstruction: "카드 클릭 시 3D 아바타/실사진 플립 | 6축 레이더 차트",
    
    // Category Tabs
    tabAll: "🔥 전체 랭킹 (K-Score)",
    tabMusic: "🎵 음원 퀸/왕 Top",
    tabAlbum: "💿 음반 제왕 Top",
    tabYoutube: "📺 유튜브 뷰왕 Top",
    tabSns: "📲 소셜 파워 Top",
    tabCheer: "💖 실시간 팬덤화력",
    tabGen5: "🌟 5세대 신예",
    tabGen4: "⚡ 4세대 대표",

    // Medals & Badges
    medal1: "🥇 1위 (Legend)",
    medal2: "🥈 2위 (Top)",
    medal3: "🥉 3위 (Elite)",
    verifiedBadge: "✓ 소속사 공식인증",
    avatarLabel: "🎨 2D 아바타 (클릭 플립)",
    photoLabel: "📸 고화질 프로필",
    chartBtn: "📊 6축 지표 차트 보기",
    cheerBtn: "💖 응원",
    cheeredDoneBtn: "💖 응원완료",

    // Modal
    chartTitle: "📊 6대 팩트 지표 레이더 차트",
    feedTitle: "💬 실시간 팬덤 한줄 토론 피드",
    nicknamePlaceholder: "닉네임",
    commentPlaceholder: "최애 응원 한줄 소통...",
    postBtn: "등록",
    noComments: "첫 응원 한줄 피드를 남겨보세요!",
    
    // Radar Labels
    radarLabels: ['음원 스트리밍 (30%)', '음반 판매량 (25%)', '유튜브 조회수 (20%)', 'SNS 성장률 (15%)', '구글 검색 버즈 (5%)', '팬덤 화력 (5%)'],

    // Support & Feedback
    supportTitle: "☕ K-Rank 개발자 후원하기",
    supportDesc: "K-Rank는 100% 팩트 데이터 기반 공정 랭킹을 유지하기 위해 부정 유료 투표 결제를 받지 않습니다. 서버 유지비 후원은 개발자에게 큰 힘이 됩니다!",
    tossBtn: "💙 토스(Toss)로 1초 후원하기",
    kakaopayBtn: "💛 카카오페이(KakaoPay)로 후원하기",

    feedbackTitle: "✉️ 의견 및 제보 보내기",
    catErr: "데이터 오류 제보",
    catAdd: "신규 아티스트 추가 요청",
    catSugg: "기능 개선 제안",
    catEtc: "기타 문의",
    fbContentPlaceholder: "상세한 의견을 입력해 주세요...",
    emailPlaceholder: "example@email.com",
    sendBtn: "보내기",

    // Methodology Page
    methTitle: "K-Score 6대 지표 산출 방법론 📐 - K-Rank",
    methMainTitle: "📐 K-Score 6-Axis Formula & Methodology",
    methDesc: "K-Rank는 주관적 인기 투표, 조작 가능성, 유료 투표 결제를 전면 배제하고, 글로벌 공식 팩트 지표(Spotify, Circle Chart, YouTube, SNS, Google Trends, 실시간 응원)만을 100점 만점으로 정량 산출합니다.",
    backToMain: "← 메인 랭킹 돌아가기",
    antiDuplicateTitle: "🛡️ 중복 부정 응원 방지 메커니즘",
    antiDuplicateDesc: "K-Rank는 매크로 및 매니아 팬덤의 부정 연타 응원을 방지하기 위해 HttpOnly Cookie (krank_vid) + Client IP/UA SHA-256 해시 듀얼 검증 시스템을 운영하며 24시간 동안 중복 투표를 원천 차단합니다."
  },

  en: {
    title: "K-Rank 🏆 - Global K-Pop Fact-Based Quantitative Leaderboard",
    tagline: "100% Fact Data Driven Global K-Pop Quantitative Ranking",
    methodologyBtn: "📐 Methodology",
    supportBtn: "☕ Support Us",
    feedbackBtn: "✉️ Feedback",
    searchPlaceholder: "Search artist, agency, fandom...",
    top3Heading: "🏆 Global Top 3 Leaders",
    top3Subheading: "(Calculated via Spotify, Circle Chart & YouTube global data)",
    seededCount: "50 Artists Live",
    gridTitleOverall: "🔥 K-Rank Overall Leaderboard",
    gridTitleMusic: "🎵 Global Music Streaming Leaderboard",
    gridTitleAlbum: "💿 Album Sales Leaderboard",
    gridTitleYoutube: "📺 YouTube MV Views Leaderboard",
    gridTitleSns: "📲 SNS Social Power Leaderboard",
    gridTitleCheer: "💖 Real-time Fandom Power Ranking",
    gridTitleGen5: "🌟 5th Gen Representative Artists",
    gridTitleGen4: "⚡ 4th Gen Representative Artists",
    cardInstruction: "Click card for 3D avatar/photo flip | 6-axis radar analysis",

    // Category Tabs
    tabAll: "🔥 Overall (K-Score)",
    tabMusic: "🎵 Music Top",
    tabAlbum: "💿 Album Top",
    tabYoutube: "📺 YouTube Top",
    tabSns: "📲 Social Power",
    tabCheer: "💖 Live Fandom Power",
    tabGen5: "🌟 5th Gen",
    tabGen4: "⚡ 4th Gen",

    // Medals & Badges
    medal1: "🥇 1st (Legend)",
    medal2: "🥈 2nd (Top)",
    medal3: "🥉 3rd (Elite)",
    verifiedBadge: "✓ Official Agency",
    avatarLabel: "🎨 2D Avatar (Click Flip)",
    photoLabel: "📸 Official Photo",
    chartBtn: "📊 View 6-Axis Chart",
    cheerBtn: "💖 Cheer",
    cheeredDoneBtn: "💖 Cheered",

    // Modal
    chartTitle: "📊 6-Axis Fact Metrics Radar Chart",
    feedTitle: "💬 Real-time Fandom Discussion Feed",
    nicknamePlaceholder: "Nickname",
    commentPlaceholder: "Share your cheer for your fav...",
    postBtn: "Post",
    noComments: "Be the first to post a cheer comment!",

    // Radar Labels
    radarLabels: ['Music Stream (30%)', 'Album Sales (25%)', 'YouTube Views (20%)', 'SNS Growth (15%)', 'Google Buzz (5%)', 'Fandom Power (5%)'],

    // Support & Feedback
    supportTitle: "☕ Support K-Rank Developers",
    supportDesc: "K-Rank does not accept paid votes to preserve 100% objective fact-based rankings. Your support helps cover server costs!",
    tossBtn: "💙 Support via Toss (Korea)",
    kakaopayBtn: "💛 Support via KakaoPay (Korea)",

    feedbackTitle: "✉️ Send Feedback / Inquiries",
    catErr: "Report Data Error",
    catAdd: "Request New Artist",
    catSugg: "Feature Suggestion",
    catEtc: "Other Inquiries",
    fbContentPlaceholder: "Enter your feedback details...",
    emailPlaceholder: "your@email.com",
    sendBtn: "Submit",

    // Methodology Page
    methTitle: "K-Score Methodology 📐 - K-Rank",
    methMainTitle: "📐 K-Score 6-Axis Formula & Methodology",
    methDesc: "K-Rank completely eliminates subjective voting, manipulation, and paid voting fees. We calculate objective K-Scores (0-100) using 100% verified global fact metrics: Spotify, Circle Chart, YouTube, SNS, Google Trends, and real-time fandom power.",
    backToMain: "← Back to Main Leaderboard",
    antiDuplicateTitle: "🛡️ Anti-Duplicate Voting Prevention",
    antiDuplicateDesc: "To prevent bot spamming and macro manipulation, K-Rank utilizes HttpOnly Cookie (krank_vid) + Client IP/UA SHA-256 dual verification to enforce a 24-hour single-cheer limit per artist."
  }
};

let currentLang = "en"; // Default to English for Global target

function initLang() {
  const saved = localStorage.getItem("krank_lang");
  if (saved && (saved === "ko" || saved === "en")) {
    currentLang = saved;
  } else {
    const userLang = navigator.language || navigator.userLanguage || "en";
    currentLang = userLang.toLowerCase().startsWith("ko") ? "ko" : "en";
  }
  applyLang(currentLang);
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("krank_lang", lang);
  applyLang(lang);
}

function t(key) {
  return (i18nDict[currentLang] && i18nDict[currentLang][key]) || i18nDict.en[key] || key;
}

function applyLang(lang) {
  document.querySelectorAll("[data-i18n]").forEach(elem => {
    const key = elem.getAttribute("data-i18n");
    if (key && i18nDict[lang] && i18nDict[lang][key]) {
      elem.innerText = i18nDict[lang][key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(elem => {
    const key = elem.getAttribute("data-i18n-placeholder");
    if (key && i18nDict[lang] && i18nDict[lang][key]) {
      elem.placeholder = i18nDict[lang][key];
    }
  });

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = lang;

  if (typeof updateDynamicTitles === "function") {
    updateDynamicTitles();
  }
}
