/* K-Rank Frontend Application Logic */

let artistsData = [];
let chartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchArtists();

  document.getElementById("searchInput").addEventListener("input", (e) => {
    fetchArtists(e.target.value.trim());
  });

  document.getElementById("closeModalBtn").addEventListener("click", closeModal);
});

async function fetchArtists(query = "") {
  try {
    const url = query ? `/api/artists?query=${encodeURIComponent(query)}` : "/api/artists";
    const res = await fetch(url);
    artistsData = await res.json();
    renderPodium(artistsData.slice(0, 3));
    renderGrid(artistsData);
  } catch (err) {
    console.error("Failed to fetch artists:", err);
  }
}

function renderPodium(top3) {
  const container = document.getElementById("podiumContainer");
  if (!top3 || top3.length === 0) {
    container.innerHTML = "";
    return;
  }

  const medals = ["🥇 1위 (Legend)", "🥈 2위 (Top)", "🥉 3위 (Elite)"];
  const bgGradients = [
    "from-amber-500/20 to-yellow-600/10 border-amber-500/40",
    "from-slate-400/20 to-slate-600/10 border-slate-400/40",
    "from-orange-600/20 to-amber-700/10 border-orange-600/40"
  ];

  container.innerHTML = top3.map((artist, idx) => `
    <div class="bg-gradient-to-b ${bgGradients[idx]} border rounded-2xl p-6 relative flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-bold px-3 py-1 rounded-full bg-slate-900/80 text-amber-300 border border-amber-500/30">
            ${medals[idx]}
          </span>
          <span class="text-xs px-2 py-0.5 rounded bg-pink-500/20 text-pink-300 font-bold border border-pink-500/30">
            K-Score ${artist.kscore}
          </span>
        </div>

        <div class="flex items-center space-x-4 mb-4">
          <div class="w-16 h-16 rounded-2xl overflow-hidden border-2 border-slate-700">
            <img src="${artist.avatar_url}" alt="${artist.name}" class="w-full h-full object-cover">
          </div>
          <div>
            <h3 class="font-extrabold text-lg text-slate-100">${artist.name}</h3>
            <p class="text-xs text-slate-400">${artist.agency} • ${artist.fandom_name}</p>
            <p class="text-xs text-pink-400 mt-1 font-semibold">${artist.signature_quote}</p>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-800/80">
        <button onclick="openDetailModal(${artist.id})" class="text-xs text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">
          📊 6축 지표 차트 보기
        </button>
        <button onclick="handleCheer(event, ${artist.id})" class="px-3 py-1.5 rounded-xl bg-pink-600/30 hover:bg-pink-600/50 text-pink-300 text-xs font-bold border border-pink-500/30 transition flex items-center gap-1">
          💖 <span id="cheer-${artist.id}">${artist.cheer_count}</span>
        </button>
      </div>
    </div>
  `).join("");
}

function renderGrid(artists) {
  const container = document.getElementById("artistGrid");
  container.innerHTML = artists.map(artist => `
    <div class="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 flex flex-col justify-between transition shadow-xl">
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-extrabold px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
            Tier ${artist.tier}
          </span>
          <span class="text-xs font-bold text-pink-400">
            Score ${artist.kscore}
          </span>
        </div>

        <!-- 3D Flip Image Container -->
        <div class="perspective w-full h-48 mb-4 cursor-pointer" onclick="toggleCardFlip(this)">
          <div class="flip-card-inner">
            <div class="flip-card-front bg-slate-800">
              <img src="${artist.avatar_url}" alt="${artist.name}" class="w-full h-full object-cover">
              <div class="absolute bottom-2 right-2 bg-slate-950/70 text-[10px] text-slate-300 px-2 py-0.5 rounded">🎨 2D 아바타 (클릭시 플립)</div>
            </div>
            <div class="flip-card-back bg-slate-800">
              <img src="${artist.photo_url}" alt="${artist.name}" class="w-full h-full object-cover">
              <div class="absolute bottom-2 right-2 bg-slate-950/70 text-[10px] text-slate-300 px-2 py-0.5 rounded">📸 공식 프로필</div>
            </div>
          </div>
        </div>

        <h3 class="font-bold text-base text-slate-100">${artist.name} <span class="text-xs text-slate-500 font-normal">(${artist.name_en})</span></h3>
        <p class="text-xs text-slate-400 mb-2">${artist.agency}</p>
        
        <div class="flex flex-wrap gap-1 mb-4">
          ${(artist.tags || []).map(tag => `<span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">${tag}</span>`).join("")}
        </div>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-slate-800">
        <button onclick="openDetailModal(${artist.id})" class="text-xs text-purple-400 hover:underline">
          📊 지표 분석
        </button>
        <button onclick="handleCheer(event, ${artist.id})" class="px-3 py-1 rounded-lg bg-pink-500/20 hover:bg-pink-500/40 text-pink-300 text-xs font-bold border border-pink-500/30 transition">
          💖 <span id="cheer-${artist.id}">${artist.cheer_count}</span>
        </button>
      </div>
    </div>
  `).join("");
}

function toggleCardFlip(elem) {
  const inner = elem.querySelector(".flip-card-inner");
  inner.classList.toggle("flipped");
}

async function handleCheer(e, artistId) {
  e.stopPropagation();
  try {
    const res = await fetch(`/api/artists/${artistId}/cheer`, { method: "POST" });
    const data = await res.json();
    const countSpan = document.getElementById(`cheer-${artistId}`);
    if (countSpan) countSpan.innerText = data.cheer_count;

    // Heart particle effect
    createHeartParticle(e.clientX, e.clientY);
  } catch (err) {
    console.error("Cheer failed:", err);
  }
}

function createHeartParticle(x, y) {
  const particle = document.createElement("div");
  particle.className = "heart-particle text-xl";
  particle.innerText = "💖";
  particle.style.left = `${x - 10}px`;
  particle.style.top = `${y - 10}px`;
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

    content.innerHTML = `
      <div class="flex items-center space-x-4 border-b border-slate-800 pb-4">
        <img src="${artist.avatar_url}" class="w-16 h-16 rounded-2xl border border-slate-700">
        <div>
          <h2 class="text-xl font-bold text-slate-100">${artist.name} (${artist.name_en})</h2>
          <p class="text-xs text-slate-400">${artist.agency} • 팬덤: ${artist.fandom_name}</p>
          <span class="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-pink-500/20 text-pink-300 font-bold">
            K-Score ${artist.kscore} (Tier ${artist.tier})
          </span>
        </div>
      </div>

      <div>
        <h3 class="text-sm font-bold text-slate-300 mb-2">📊 6대 팩트 지표 레이더 차트</h3>
        <div class="w-full h-64 flex justify-center">
          <canvas id="radarChartCanvas"></canvas>
        </div>
      </div>
    `;

    renderRadarChart(artist.stats);
  } catch (err) {
    console.error("Failed to load modal:", err);
  }
}

function renderRadarChart(stats) {
  const ctx = document.getElementById("radarChartCanvas").getContext("2d");
  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['음원 스트리밍 (30%)', '음반 판매량 (25%)', '유튜브 조회수 (20%)', 'SNS 성장률 (15%)', '구글 검색 버즈 (5%)', '팬덤 화력 (5%)'],
      datasets: [{
        label: '6대 정량 지표 점수',
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
