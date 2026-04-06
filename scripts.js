const imageFiles = [
  "001.webp",
  "002.webp",
  "003.webp",
  "004.webp",
  "005.webp",
  "006.webp",
  "007.webp",
  "008.webp",
  "009.webp",
  "010.webp",
  "011.webp",
  "012.webp",
  "013.webp",
  "014.webp",
  "015.webp",
  "016.webp",
  "017.webp",
  "018.webp",
  "019.webp",
  "020.webp",
  "021.webp",
  "022.webp",
  "023.webp",
  "024.webp",
  "025.webp",
  "026.webp",
  "027.webp",
  "028.webp",
  "029.webp",
  "030.webp",
  "031.webp",
  "032.webp",
  "033.webp",
  "034.webp",
  "035.webp",
  "036.webp",
  "037.webp",
  "038.webp",
  "039.webp",
  "040.webp",
  "041.webp",
  "042.webp",
];

const messageEl = document.getElementById("coffee-message");
const countdownEl = document.getElementById("coffee-countdown");
const TIME_ZONE = "America/New_York";

function getZonedParts(date, timeZone) {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "numeric",
    day: "numeric",
    weekday: "short",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    hour12: false,
  });

  const parts = formatter.formatToParts(date);
  const out = {};

  for (const part of parts) {
    if (part.type !== "literal") {
      out[part.type] = part.value;
    }
  }

  return {
    year: Number(out.year),
    month: Number(out.month),
    day: Number(out.day),
    hour: Number(out.hour),
    minute: Number(out.minute),
    second: Number(out.second),
    weekday: out.weekday,
  };
}

function getCurrentTimeInZone(timeZone) {
  const now = new Date();
  const parts = getZonedParts(now, timeZone);

  return {
    now,
    ...parts,
  };
}

function getNextFriday8am(timeZone) {
  const now = new Date();
  const zoned = getZonedParts(now, timeZone);

  const weekdayMap = {
    Sun: 0,
    Mon: 1,
    Tue: 2,
    Wed: 3,
    Thu: 4,
    Fri: 5,
    Sat: 6,
  };

  const currentDay = weekdayMap[zoned.weekday];
  const friday = 5;

  let daysUntilFriday = (friday - currentDay + 7) % 7;

  const isFridayAfterOrAt8 =
    currentDay === friday &&
    (zoned.hour > 8 || (zoned.hour === 8 && zoned.minute >= 0) || zoned.hour >= 9 || zoned.hour >= 10);

  if (currentDay === friday && zoned.hour >= 8) {
    daysUntilFriday = 7;
  }

  const target = new Date(now);
  target.setUTCDate(target.getUTCDate() + daysUntilFriday);

  const targetParts = getZonedParts(target, timeZone);

  const approxTarget = new Date(Date.UTC(targetParts.year, targetParts.month - 1, targetParts.day, 8, 0, 0));

  const offsetGuess = new Date(approxTarget.toLocaleString("en-US", { timeZone }));
  const actualTarget = new Date(approxTarget.getTime() + (approxTarget.getTime() - offsetGuess.getTime()));

  return actualTarget;
}

function isCoffeeCurrentlyHappening(timeZone) {
  const zoned = getCurrentTimeInZone(timeZone);
  return zoned.weekday === "Fri" && zoned.hour >= 8 && zoned.hour < 10;
}

function formatCountdown(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

function updateCoffeeTimer() {
  if (isCoffeeCurrentlyHappening(TIME_ZONE)) {
    countdownEl.textContent = "we are currently drinking coffee outside";
    messageEl.style.display = "none";
    return;
  }

  const now = new Date();
  const nextFriday = getNextFriday8am(TIME_ZONE);
  const diff = nextFriday - now;

  messageEl.textContent = "we will be drinking coffee outside in";
  countdownEl.textContent = formatCountdown(diff);
  countdownEl.style.display = "block";
}

function shuffleArray(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function getRowCount() {
  const h = window.innerHeight;

  if (h < 500) return 2;
  if (h < 900) return 3;
  return 4;
}

function getSizeClass() {
  const roll = Math.random();

  if (roll < 0.14) return "featured";
  if (roll < 0.38) return "wide";
  if (roll < 0.62) return "tall";
  return "standard";
}

function buildRow(rowImages, rowIndex) {
  const row = document.createElement("div");
  row.className = `photo-row row-${rowIndex + 1}`;

  const track = document.createElement("div");
  track.className = "photo-track";

  const rowSet = [...rowImages, ...rowImages];

  rowSet.forEach((file) => {
    const item = document.createElement("div");
    item.className = `photo-item ${getSizeClass()}`;

    const img = document.createElement("img");
    img.src = `media/instagram/${file}`;
    img.alt = "";
    img.loading = "lazy";

    item.appendChild(img);
    track.appendChild(item);
  });

  row.appendChild(track);
  return row;
}

function splitIntoRows(images, rows) {
  const buckets = Array.from({ length: rows }, () => []);

  images.forEach((file, index) => {
    buckets[index % rows].push(file);
  });

  return buckets;
}

function loadImages() {
  const collage = document.getElementById("photo-collage");
  if (!collage) return;

  collage.innerHTML = "";

  const rows = getRowCount();
  const shuffled = shuffleArray(imageFiles);
  const rowGroups = splitIntoRows(shuffled, rows);

  rowGroups.forEach((rowImages, i) => {
    if (rowImages.length > 0) {
      collage.appendChild(buildRow(rowImages, i));
    }
  });
}

let resizeTimer;

window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    loadImages();
  }, 200);
});

document.addEventListener("DOMContentLoaded", () => {
  updateCoffeeTimer();
  loadImages();
  setInterval(updateCoffeeTimer, 1000);
});
