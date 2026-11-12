/* K-Rank Frontend Application Logic (v2.0 Global i18n) */

let artistsData = [];
let myCheeredArtistIds = new Set();
let chartInstance = null;
let currentSort = "kscore";
let currentGen = "";

document.addEventListener("DOMContentLoaded", () => {
  if (typeof initLang === "function") {
    initLang();
  }
  fetchMyCheers();
  fetchArtists();

  document.getElementById("searchInput").addEventListener("input", (e) => {
    fetchArtists(e.target.value.trim());
  });

  document.getElementById("closeModalBtn").addEventListener("click", closeModal);

  // Theme toggle
  const themeToggle = document.getElementById("themeToggle");
  const themeToggleMobile = document.getElementById("themeToggleMobile");
  if (themeToggle) themeToggle.addEventListener("click", toggleTheme);
  if (themeToggleMobile) themeToggleMobile.addEventListener("click", toggleTheme);

  // Initial Theme Load
  if (localStorage.getItem("krank_theme") === "light") {
    document.body.classList.remove("bg-slate-950", "text-slate-100");
    document.body.classList.add("bg-slate-100", "text-slate-900");
  }
});

async function fetchMyCheers() {
  try {
    const res = await fetch("/api/my-cheers");
    const ids = await res.json();
    myCheeredArtistIds = new Set(ids);
  } catch (err) {
    console.error("Failed to fetch my cheers:", err);
  }
}

async function fetchArtists(query = "") {
  try {
    let url = `/api/artists?sort=${currentSort}`;
    if (query) url += `&query=${encodeURIComponent(query)}`;
    if (currentGen) url += `&gen=${encodeURIComponent(currentGen)}`;

    const res = await fetch(url);
    artistsData = await res.json();

    renderPodium(artistsData.slice(0, 3));
    renderGrid(artistsData);
  } catch (err) {
    console.error("Failed to fetch artists:", err);
  }
}

function updateDynamicTitles() {
  const titles = {
    all: typeof t === "function" ? t("gridTitleOverall") : "🔥 Overall Leaderboard",
    music: typeof t === "function" ? t("gridTitleMusic") : "🎵 Music Stream Top",
    album: typeof t === "function" ? t("gridTitleAlbum") : "💿 Album Sales Top",
    youtube: typeof t === "function" ? t("gridTitleYoutube") : "📺 YouTube Views Top",
    sns: typeof t === "function" ? t("gridTitleSns") : "📲 Social Power Top",
    cheer: typeof t === "function" ? t("gridTitleCheer") : "💖 Live Fandom Power"
  };
  
  if (currentGen) {
    const genTitle = currentGen === "5세대" ? (typeof t === "function" ? t("gridTitleGen5") : "🌟 5th Gen") : (typeof t === "function" ? t("gridTitleGen4") : "⚡ 4th Gen");
    document.getElementById("gridTitle").innerText = genTitle;
  } else {
    document.getElementById("gridTitle").innerText = titles[currentSort] || titles.all;
  }

  if (artistsData && artistsData.length > 0) {
    renderPodium(artistsData.slice(0, 3));
    renderGrid(artistsData);
  }
}

function filterCategory(sortKey) {
  currentSort = sortKey;
  currentGen = "";

  document.querySelectorAll(".cat-btn").forEach(btn => {
    if (btn.dataset.cat === sortKey) {
      btn.className = "cat-btn px-3 py-1.5 rounded-lg bg-pink-500 text-white font-bold transition whitespace-nowrap";
    } else {
      btn.className = "cat-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-400 font-semibold hover:bg-slate-700 transition whitespace-nowrap";
    }
  });

  document.querySelectorAll(".gen-btn").forEach(btn => {
    btn.className = "gen-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-400 font-semibold hover:bg-slate-700 transition whitespace-nowrap";
  });

  updateDynamicTitles();
  fetchArtists(document.getElementById("searchInput").value.trim());
}

function filterGen(genKey) {
  currentGen = genKey;
  currentSort = "kscore";

  document.querySelectorAll(".gen-btn").forEach(btn => {
    if (btn.dataset.gen === genKey) {
      btn.className = "gen-btn px-3 py-1.5 rounded-lg bg-purple-600 text-white font-bold transition whitespace-nowrap";
    } else {
      btn.className = "gen-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-400 font-semibold hover:bg-slate-700 transition whitespace-nowrap";
    }
  });

  updateDynamicTitles();
  fetchArtists(document.getElementById("searchInput").value.trim());
}

function renderPodium(top3) {
  const container = document.getElementById("podiumContainer");
  if (!top3 || top3.length === 0) {
    container.innerHTML = "";
    return;
  }

  const medals = [
    typeof t === "function" ? t("medal1") : "🥇 1st",
    typeof t === "function" ? t("medal2") : "🥈 2nd",
    typeof t === "function" ? t("medal3") : "🥉 3rd"
  ];
  const bgGradients = [
    "from-amber-500/20 to-yellow-600/10 border-amber-500/40",
    "from-slate-400/20 to-slate-600/10 border-slate-400/40",
    "from-orange-600/20 to-amber-700/10 border-orange-600/40"
  ];

  container.innerHTML = top3.map((artist, idx) => {
    const isCheered = myCheeredArtistIds.has(artist.id);
    const verifiedTxt = typeof t === "function" ? t("verifiedBadge") : "✓ Verified";
    const chartTxt = typeof t === "function" ? t("chartBtn") : "📊 Chart";
    const cheerTxt = isCheered ? (typeof t === "function" ? t("cheeredDoneBtn") : "💖 Cheered") : (typeof t === "function" ? t("cheerBtn") : "💖 Cheer");

    return `
    <div class="bg-gradient-to-b ${bgGradients[idx]} border rounded-2xl p-6 relative flex flex-col justify-between shadow-xl">
      <div>
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-bold px-3 py-1 rounded-full bg-slate-900/80 text-amber-300 border border-amber-500/30">
            ${medals[idx]}
          </span>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-pink-500/20 text-pink-300 font-black border border-pink-500/30">
            K-Score ${artist.kscore}
          </span>
        </div>

        <div class="flex items-center space-x-4 mb-4">
          <div class="w-16 h-16 rounded-2xl overflow-hidden border-2 border-slate-700 shadow-md">
            <img src="${artist.avatar_url}" alt="${artist.name}" referrerpolicy="no-referrer" class="w-full h-full object-cover">
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h3 class="font-extrabold text-lg text-slate-100">${currentLang === 'en' ? (artist.name_en || artist.name) : artist.name}</h3>
              ${artist.is_verified ? `<span class="text-[10px] px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30">${verifiedTxt}</span>` : ''}
            </div>
            <p class="text-xs text-slate-400">${currentLang === 'en' ? (artist.agency_en || artist.agency) : artist.agency} • ${currentLang === 'en' ? (artist.fandom_name_en || artist.fandom_name) : artist.fandom_name}</p>
            <p class="text-xs text-pink-400 mt-1 font-semibold italic">"${currentLang === 'en' ? (artist.signature_quote_en || artist.signature_quote) : artist.signature_quote}"</p>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-800/80">
        <button onclick="openDetailModal(${artist.id})" class="text-xs text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">
          ${chartTxt}
        </button>
        <button onclick="handleCheer(event, ${artist.id})" 
                class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                  isCheered 
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' 
                  : 'bg-pink-600/30 hover:bg-pink-600/50 text-pink-300 border border-pink-500/30 shadow-md'
                }">
          ${cheerTxt} <span id="cheer-${artist.id}">${artist.cheer_count}</span>
        </button>
      </div>
    </div>
  `;
  }).join("");
}

function renderGrid(artists) {
  const container = document.getElementById("artistGrid");
  container.innerHTML = artists.map(artist => {
    const isCheered = myCheeredArtistIds.has(artist.id);
    const cheerTxt = isCheered ? (typeof t === "function" ? t("cheeredDoneBtn") : "💖 Cheered") : (typeof t === "function" ? t("cheerBtn") : "💖 Cheer");
    const avatarLbl = typeof t === "function" ? t("avatarLabel") : "🎨 2D Avatar";
    const photoLbl = typeof t === "function" ? t("photoLabel") : "📸 Official Photo";

    return `
    <div class="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 flex flex-col justify-between transition shadow-xl hover:shadow-2xl">
      <div>
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-extrabold px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Tier ${artist.tier}
            </span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">
              ${currentLang === 'en' ? (artist.generation_en || artist.generation) : artist.generation}
            </span>
          </div>
          <span class="text-xs font-black text-pink-400">
            Score ${artist.kscore}
          </span>
        </div>

        <!-- 3D Flip Image Container -->
        <div class="perspective w-full h-48 mb-4 cursor-pointer" onclick="toggleCardFlip(this)">
          <div class="flip-card-inner">
            <div class="flip-card-front bg-slate-800 rounded-xl overflow-hidden border border-slate-700/60">
              <img src="${artist.avatar_url}" alt="${artist.name}" referrerpolicy="no-referrer" class="w-full h-full object-cover">
              <div class="absolute bottom-2 right-2 bg-slate-950/80 text-[10px] text-slate-300 px-2 py-0.5 rounded-md border border-slate-700">${avatarLbl}</div>
            </div>
            <div class="flip-card-back bg-slate-800 rounded-xl overflow-hidden border border-slate-700/60">
              <img src="${artist.photo_url}" alt="${artist.name}" referrerpolicy="no-referrer" class="w-full h-full object-cover">
              <div class="absolute bottom-2 right-2 bg-slate-950/80 text-[10px] text-pink-300 font-bold px-2 py-0.5 rounded-md border border-pink-500/30">${photoLbl}</div>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-1.5 mb-1">
          <h3 class="font-extrabold text-base text-slate-100">${currentLang === 'en' ? artist.name_en : artist.name}</h3>
          <span class="text-xs text-slate-500 font-normal">(${currentLang === 'en' ? artist.name : artist.name_en})</span>
          ${artist.is_verified ? `<span class="text-[10px] text-blue-400" title="Verified">✓</span>` : ''}
        </div>
        <p class="text-xs text-slate-400 mb-2">${currentLang === 'en' ? (artist.agency_en || artist.agency) : artist.agency}</p>
        
        <div class="flex flex-wrap gap-1 mb-4">
          ${(currentLang === 'en' && artist.tags_en && artist.tags_en.length ? artist.tags_en : artist.tags || []).map(tag => `<span class="text-[10px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/50">${tag}</span>`).join("")}
        </div>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-slate-800/80">
        <button onclick="openDetailModal(${artist.id})" class="text-xs text-purple-400 hover:text-purple-300 font-semibold">
          📊 ${typeof t === 'function' ? t('chartBtn') : 'Chart'}
        </button>
        <button onclick="handleCheer(event, ${artist.id})" 
                class="px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                  isCheered 
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' 
                  : 'bg-pink-600/30 hover:bg-pink-600/50 text-pink-300 border border-pink-500/30'
                }">
          ${cheerTxt} <span id="cheer-${artist.id}">${artist.cheer_count}</span>
        </button>
      </div>
    </div>
  `;
  }).join("");
}

function toggleCardFlip(elem) {
  const inner = elem.querySelector(".flip-card-inner");
  inner.classList.toggle("flipped");
}

async function handleCheer(e, artistId) {
  e.stopPropagation();
  if (myCheeredArtistIds.has(artistId)) {
    alert(currentLang === 'ko' ? "이미 오늘 해당 아티스트를 응원하셨습니다!" : "You have already cheered for this artist today!");
    return;
  }

  try {
    const res = await fetch(`/api/artists/${artistId}/cheer`, { method: "POST" });
    if (res.status === 409) {
      alert(currentLang === 'ko' ? "이미 응원하셨습니다 (1일 1회 제약)." : "Already cheered today (1 per day limit).");
      myCheeredArtistIds.add(artistId);
      fetchArtists(document.getElementById("searchInput").value.trim());
      return;
    }

    const data = await res.json();
    myCheeredArtistIds.add(artistId);

    createHeartParticle(e.clientX, e.clientY);
    fetchArtists(document.getElementById("searchInput").value.trim());
  } catch (err) {
    console.error("Cheer failed:", err);
  }
}

function createHeartParticle(x, y) {
  const particle = document.createElement("div");
  particle.className = "heart-particle text-2xl z-50 fixed pointer-events-none";
  particle.innerText = "💖";
  particle.style.left = `${x - 12}px`;
  particle.style.top = `${y - 12}px`;
  document.body.appendChild(particle);
  setTimeout(() => particle.remove(), 800);
}

async function openDetailModal(artistId) {
  const modal = document.getElementById("detailModal");
  const content = document.getElementById("modalContent");
  modal.classList.remove("hidden");
  modal.classList.add("flex");

  try {
    const res = await fetch(`/api/artists/${artistId}`);
    const artist = await res.json();

    const discRes = await fetch(`/api/artists/${artistId}/discussions`);
    const discussions = await discRes.json();

    content.innerHTML = `
      <div class="flex items-center space-x-4 border-b border-slate-800 pb-4">
        <img src="${artist.avatar_url}" class="w-16 h-16 rounded-2xl border border-slate-700">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-xl font-bold text-slate-100">${currentLang === 'en' ? artist.name_en : artist.name} (${currentLang === 'en' ? artist.name : artist.name_en})</h2>
            ${artist.is_verified ? `<span class="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30">${typeof t === 'function' ? t('verifiedBadge') : '✓ Verified'}</span>` : ''}
          </div>
          <p class="text-xs text-slate-400">${currentLang === 'en' ? (artist.agency_en || artist.agency) : artist.agency} • Fandom: ${currentLang === 'en' ? (artist.fandom_name_en || artist.fandom_name) : artist.fandom_name}</p>
          <span class="inline-block mt-1 text-xs px-2.5 py-0.5 rounded-full bg-pink-500/20 text-pink-300 font-bold border border-pink-500/30">
            K-Score ${artist.kscore} (Tier ${artist.tier})
          </span>
        </div>
      </div>

      <div>
        <h3 class="text-sm font-bold text-slate-300 mb-2">${typeof t === 'function' ? t('chartTitle') : '📊 6-Axis Radar Chart'}</h3>
        <div class="w-full h-64 flex justify-center">
          <canvas id="radarChartCanvas"></canvas>
        </div>
      </div>

      <!-- Fan Discussion Feed -->
      <div class="border-t border-slate-800 pt-4 space-y-3">
        <h3 class="text-sm font-bold text-slate-300">${typeof t === 'function' ? t('feedTitle') : '💬 Fandom Discussion Feed'}</h3>
        
        <div class="flex gap-2">
          <input type="text" id="discAuthor" placeholder="${typeof t === 'function' ? t('nicknamePlaceholder') : 'Nickname'}" class="w-28 bg-slate-800 border border-slate-700 text-xs rounded-xl p-2 text-slate-200">
          <input type="text" id="discContent" placeholder="${typeof t === 'function' ? t('commentPlaceholder') : 'Share comment...'}" class="flex-1 bg-slate-800 border border-slate-700 text-xs rounded-xl p-2 text-slate-200">
          <button onclick="submitDiscussion(${artist.id})" class="px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs rounded-xl transition">
            ${typeof t === 'function' ? t('postBtn') : 'Post'}
          </button>
        </div>

        <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
          ${discussions.length === 0 ? `<p class="text-xs text-slate-500 py-2">${typeof t === 'function' ? t('noComments') : 'No comments yet.'}</p>` : discussions.map(d => `
            <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs space-y-1">
              <div class="flex items-center justify-between text-slate-400">
                <span class="font-bold text-slate-200">${d.author} ${d.is_official ? '<span class="text-[10px] text-blue-400 font-bold">[Official]</span>' : ''}</span>
                <span class="text-[10px]">${(d.created_at || '').substring(0, 16)}</span>
              </div>
              <p class="text-slate-300">${d.content}</p>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    renderRadarChart(artist.stats);
  } catch (err) {
    console.error("Failed to load modal:", err);
  }
}

async function submitDiscussion(artistId) {
  const author = document.getElementById("discAuthor").value.trim() || (currentLang === 'ko' ? "익명팬덤" : "Anonymous Fan");
  const content = document.getElementById("discContent").value.trim();
  if (!content) return alert(currentLang === 'ko' ? "내용을 입력해 주세요." : "Please enter comment details.");

  try {
    await fetch(`/api/artists/${artistId}/discussions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ author, content, stance: "💖 응원" })
    });
    openDetailModal(artistId);
  } catch (err) {
    console.error("Failed to post discussion:", err);
  }
}

function renderRadarChart(stats) {
  const ctx = document.getElementById("radarChartCanvas").getContext("2d");
  if (chartInstance) chartInstance.destroy();

  const labels = (typeof t === 'function' && i18nDict[currentLang] && i18nDict[currentLang].radarLabels)
    ? i18nDict[currentLang].radarLabels
    : ['Music Stream (30%)', 'Album Sales (25%)', 'YouTube Views (20%)', 'SNS Growth (15%)', 'Google Buzz (5%)', 'Fandom Power (5%)'];

  chartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'K-Score Fact Metrics',
        data: [
          stats.music_stream || 50,
          stats.album_sales || 50,
          stats.youtube_views || 50,
          stats.sns_growth || 50,
          stats.google_buzz || 50,
          stats.fandom_power || 50
        ],
        backgroundColor: 'rgba(236, 72, 153, 0.25)',
        borderColor: 'rgba(236, 72, 153, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(236, 72, 153, 1)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          pointLabels: { color: '#cbd5e1', font: { size: 11 } },
          ticks: { backdropColor: 'transparent', color: '#64748b' },
          min: 0,
          max: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function closeModal() {
  const modal = document.getElementById("detailModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function openSupportModal() {
  const m = document.getElementById("supportModal");
  m.classList.remove("hidden");
  m.classList.add("flex");
}

function closeSupportModal() {
  const m = document.getElementById("supportModal");
  m.classList.add("hidden");
  m.classList.remove("flex");
}

function openFeedbackModal() {
  const m = document.getElementById("feedbackModal");
  m.classList.remove("hidden");
  m.classList.add("flex");
}

function closeFeedbackModal() {
  const m = document.getElementById("feedbackModal");
  m.classList.add("hidden");
  m.classList.remove("flex");
}

async function submitFeedback() {
  const category = document.getElementById("fbCategory").value;
  const content = document.getElementById("fbContent").value.trim();
  const email = document.getElementById("fbEmail").value.trim();

  if (!content) return alert(currentLang === 'ko' ? "의견 내용을 입력해 주세요." : "Please enter feedback details.");

  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, content, email })
    });
    alert(currentLang === 'ko' ? "소중한 의견이 제출되었습니다. 감사합니다!" : "Thank you for your feedback!");
    closeFeedbackModal();
  } catch (err) {
    console.error("Feedback failed:", err);
  }
}

function toggleTheme() {
  if (document.body.classList.contains("bg-slate-950")) {
    document.body.classList.remove("bg-slate-950", "text-slate-100");
    document.body.classList.add("bg-slate-100", "text-slate-900");
    localStorage.setItem("krank_theme", "light");
  } else {
    document.body.classList.remove("bg-slate-100", "text-slate-900");
    document.body.classList.add("bg-slate-950", "text-slate-100");
    localStorage.setItem("krank_theme", "dark");
  }
}
