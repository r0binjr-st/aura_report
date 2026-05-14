const steps = [...document.querySelectorAll(".step")];
const form = document.querySelector("#auraForm");
const resultPanel = document.querySelector("#resultPanel");
const photoInput = document.querySelector("#photos");
const photoLabel = document.querySelector("#photoLabel");
const uploadZone = document.querySelector(".upload-zone");
const statusLabel = document.querySelector("#statusLabel");
const loadingMessage = document.querySelector("#loadingMessage");
const reportCard = document.querySelector("#reportCard");
const AURA_SESSION_KEY = "aura-report-session";

const loadingMessages = [
  "слушаем, как ник кашляет в подъезде...",
  "ищем SoundCloud-вкус в плейлисте...",
  "меряем арку злодея рулеткой из ларька...",
  "считаем сорок тысяч в воздухе...",
  "проверяем Химки на утрату телефона...",
  "ищем потапычев след в мягкой части души...",
  "вызываем Марка Година в воображаемый кабинет...",
  "считаем М М, красная лампа уже горит...",
];

let currentStep = 0;
let loadingTimer = null;
let lastReport = null;
let photoPreviewUrl = null;

function showStep(index) {
  currentStep = Math.max(0, Math.min(index, steps.length - 1));
  steps.forEach((step) => step.classList.toggle("active", Number(step.dataset.step) === currentStep));
  saveAuraSession();
}

function validateStep(index) {
  if (index === 2) return document.querySelector("#nickname").reportValidity();
  if (index === 3) return document.querySelector("#music").reportValidity();
  if (index === 4) return document.querySelector("#freeform_text").reportValidity();
  return true;
}

document.querySelectorAll("[data-next]").forEach((button) => {
  button.addEventListener("click", () => {
    if (validateStep(currentStep)) showStep(currentStep + 1);
  });
});

document.querySelectorAll("[data-prev]").forEach((button) => {
  button.addEventListener("click", () => showStep(currentStep - 1));
});

form.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" || event.shiftKey) return;

  const submitStep = currentStep === 4;
  if (!submitStep && currentStep < 2) return;

  event.preventDefault();
  if (!validateStep(currentStep)) return;

  if (submitStep) {
    form.requestSubmit();
    return;
  }

  showStep(currentStep + 1);
});

function updatePhotoSelection() {
  const count = Math.min(photoInput.files.length, 3);
  photoLabel.textContent = count ? `улики приняты: ${count}` : "выбрать фото";
  if (photoPreviewUrl) URL.revokeObjectURL(photoPreviewUrl);
  photoPreviewUrl = count ? URL.createObjectURL(photoInput.files[0]) : null;
  if (photoInput.files.length > 3) {
    statusLabel.textContent = "лишние фото ушли в подъезд";
  }
}

function imageFilesFromDrop(event) {
  const items = [...(event.dataTransfer.items || [])]
    .filter((item) => item.kind === "file")
    .map((item) => item.getAsFile())
    .filter(Boolean);
  const files = items.length ? items : [...event.dataTransfer.files];
  return files.filter((file) => file.type.startsWith("image/"));
}

function setSelectedPhotos(files, append = false) {
  const current = append ? [...photoInput.files] : [];
  const merged = [...current, ...files.filter((file) => file.type.startsWith("image/"))];
  const unique = merged.filter((file, index, list) => {
    return (
      index ===
      list.findIndex((candidate) => {
        return (
          candidate.name === file.name &&
          candidate.size === file.size &&
          candidate.lastModified === file.lastModified
        );
      })
    );
  });
  const images = unique.slice(0, 3);
  const transfer = new DataTransfer();
  images.forEach((file) => transfer.items.add(file));
  photoInput.files = transfer.files;
  updatePhotoSelection();
}

photoInput.addEventListener("change", updatePhotoSelection);

["dragenter", "dragover"].forEach((eventName) => {
  uploadZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadZone.classList.add("drag-over");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadZone.classList.remove("drag-over");
  });
});

uploadZone.addEventListener("drop", (event) => {
  setSelectedPhotos(imageFilesFromDrop(event), true);
});

function startLoading() {
  let index = 0;
  showStep(5);
  loadingMessage.textContent = loadingMessages[index];
  loadingTimer = setInterval(() => {
    index = (index + 1) % loadingMessages.length;
    loadingMessage.textContent = loadingMessages[index];
  }, 850);
}

function stopLoading() {
  clearInterval(loadingTimer);
  loadingTimer = null;
}

function renderStats(stats) {
  const container = document.querySelector("#stats");
  container.innerHTML = "";
  Object.entries(stats).forEach(([name, value]) => {
    const row = document.createElement("div");
    row.className = `stat-row ${statClass(name)} ${statHeat(value)}`;
    row.innerHTML = `
      <div class="stat-label"><span>${name}</span><strong>${value}%</strong></div>
      <div class="stat-hint">${statCaption(name, value)}</div>
      <div class="bar"><i style="width: ${value}%"></i></div>
    `;
    container.appendChild(row);
  });
}

function statClass(name) {
  const classes = {
    "арка злодея": "stat-villain",
    "темный друн": "stat-drun",
    "секс маньяк": "stat-flirt",
    "М М": "stat-mm",
    "потапыч R.I.P": "stat-potapych",
    "артем коршунов (джокер)": "stat-joker",
    "саша епифановский": "stat-sasha",
    "сигма синдром": "stat-sigma",
  };
  return classes[name] || "stat-unknown";
}

function statHeat(value) {
  if (value >= 85) return "heat-critical";
  if (value >= 65) return "heat-loud";
  if (value <= 18) return "heat-dead";
  return "heat-weird";
}

function statCaption(name, value) {
  const captions = {
    "арка злодея": "плащ проверен, банкомат молчит",
    "темный друн": "тиктошная философия пахнет сорока тысячами",
    "секс маньяк": "романтическая сигнализация без лицензии",
    "М М": "эмоциональная сирена и дымок сюжета",
    "потапыч R.I.P": "хомячий траурный индекс",
    "артем коршунов (джокер)": "ирония открыла филиал",
    "саша епифановский": "апокалипсис в тапках",
    "сигма синдром": "турник просит паузу",
  };
  const heat = value >= 85 ? " / критический перегрев" : value <= 18 ? " / почти не дышит" : "";
  return `${captions[name] || "симптом без паспорта"}${heat}`;
}

function renderExplanation(text) {
  const container = document.querySelector("#explanation");
  const sentences = text
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
  container.innerHTML = sentences.map((sentence) => `<p>${sentence}</p>`).join("");
}

function renderUploadedPhoto() {
  const image = document.querySelector("#uploadedPhotoPreview");
  const caption = document.querySelector("#uploadedPhotoCaption");
  if (photoPreviewUrl) {
    image.src = photoPreviewUrl;
    image.hidden = false;
    caption.textContent = "первый кадр назначен старшим по абсурду";
    return;
  }

  image.removeAttribute("src");
  image.hidden = true;
  caption.textContent = "фото нет, значит лицо дела рисует сама тревога";
}

function renderAuraNote(report) {
  const note = document.querySelector("#auraNoteText");
  const legend = document.querySelector("#auraNoteLegend");
  if (!note || !legend) return;

  const sorted = Object.entries(report.stats).sort((a, b) => b[1] - a[1]);
  const [topName, topValue] = sorted[0];
  const [secondName, secondValue] = sorted[1];
  const [lowName, lowValue] = sorted[sorted.length - 1];

  const noteLines = {
    "арка злодея": "плащ уже в кадре, причина пока ищет парковку",
    "темный друн": "SoundCloud-вкус и тикток-философия делают вид, что это судьба",
    "секс маньяк": "флирт-датчик орет, но это всё еще не уголовка, а театр сигнала",
    "М М": "красная лампа сюжета мигает, эмоциональная стабильность вышла из чата",
    "потапыч R.I.P": "хомячий след найден, протокол просит минуту тишины",
    "артем коршунов (джокер)": "ирония открыла филиал и назначила себя директором",
    "саша епифановский": "апокалипсис в тапках вышел на сцену с мокрым пакетом",
    "сигма синдром": "саморазвитие чинит лифт, которого нет",
  };

  note.textContent = `Главный шум: «${topName}» ${topValue}%. ${noteLines[topName] || "Анкета нашла главный перегрев и сделала вид, что так было."}`;
  legend.textContent = `Второй свидетель: «${secondName}» ${secondValue}%. Слабое место: «${lowName}» ${lowValue}%. Машина верит громким симптомам, а не среднему киселю.`;
}

function renderReport(report) {
  lastReport = report;
  document.querySelector("#resultNickname").textContent = `@${document.querySelector("#nickname").value.trim() || "unknown.exe"}`;
  document.querySelector("#archetype").textContent = report.archetype;
  document.querySelector("#mentalState").textContent = report.mental_state;
  document.querySelector("#location").textContent = report.location;
  document.querySelector("#diagnosis").textContent = report.diagnosis;
  renderExplanation(report.explanation);
  renderUploadedPhoto();
  renderAuraNote(report);
  renderStats(report.stats);
  showStep(6);
  resultPanel.hidden = false;
  statusLabel.textContent = report.analysis_source || "report generated";
  saveAuraSession();
}

function reportToText(report) {
  const nick = document.querySelector("#nickname").value.trim() || "unknown.exe";
  const stats = Object.entries(report.stats)
    .map(([name, value]) => `${name}: ${value}%`)
    .join("\n");
  return `AURA REPORT\n@${nick}\n\nличное дело: ${report.archetype}\n\n${stats}\n\nрежим головы: ${report.mental_state}\nместо падения: ${report.location}\nкороткий приговор: ${report.diagnosis}\n\n${report.explanation}`;
}

function formSnapshot() {
  return {
    nickname: document.querySelector("#nickname").value,
    music: document.querySelector("#music").value,
    freeform_text: document.querySelector("#freeform_text").value,
  };
}

function restoreFormSnapshot(values = {}) {
  document.querySelector("#nickname").value = values.nickname || "";
  document.querySelector("#music").value = values.music || "";
  document.querySelector("#freeform_text").value = values.freeform_text || "";
}

function saveAuraSession() {
  sessionStorage.setItem(
    AURA_SESSION_KEY,
    JSON.stringify({
      step: currentStep,
      form: formSnapshot(),
      report: lastReport,
      resultVisible: !resultPanel.hidden,
    })
  );
}

function restoreAuraSession() {
  const raw = sessionStorage.getItem(AURA_SESSION_KEY);
  if (!raw) return false;

  try {
    const saved = JSON.parse(raw);
    restoreFormSnapshot(saved.form);
    if (saved.report && saved.resultVisible) {
      renderReport(saved.report);
      return true;
    }
    showStep(saved.step || 0);
    return true;
  } catch {
    sessionStorage.removeItem(AURA_SESSION_KEY);
    return false;
  }
}

function inlineComputedStyles(source, target) {
  const computed = window.getComputedStyle(source);
  const styleText = [...computed].map((name) => `${name}:${computed.getPropertyValue(name)};`).join("");
  target.setAttribute("style", styleText);

  [...source.children].forEach((child, index) => {
    inlineComputedStyles(child, target.children[index]);
  });
}

async function downloadReportImage() {
  if (!lastReport || !reportCard) return;

  const bounds = reportCard.getBoundingClientRect();
  const clone = reportCard.cloneNode(true);
  inlineComputedStyles(reportCard, clone);
  clone.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${bounds.width}" height="${bounds.height}">
      <foreignObject width="100%" height="100%">${new XMLSerializer().serializeToString(clone)}</foreignObject>
    </svg>
  `;
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }));
  const image = new Image();
  image.src = url;
  await image.decode();

  const scale = Math.max(2, window.devicePixelRatio || 1);
  const canvas = document.createElement("canvas");
  canvas.width = Math.ceil(bounds.width * scale);
  canvas.height = Math.ceil(bounds.height * scale);
  const context = canvas.getContext("2d");
  context.scale(scale, scale);
  context.drawImage(image, 0, 0);
  URL.revokeObjectURL(url);

  const link = document.createElement("a");
  const nick = document.querySelector("#nickname").value.trim() || "unknown";
  link.download = `aura-report-${nick.replace(/[^\w-]+/g, "_")}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
  statusLabel.textContent = "карточка скачана";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!validateStep(4)) return;

  const data = new FormData();
  [...photoInput.files].slice(0, 3).forEach((file) => data.append("photos", file));
  data.append("nickname", document.querySelector("#nickname").value.trim());
  data.append("music", document.querySelector("#music").value.trim());
  data.append("freeform_text", document.querySelector("#freeform_text").value.trim());

  startLoading();
  resultPanel.hidden = true;

  try {
    const response = await fetch("/api/aura/analyze", {
      method: "POST",
      body: data,
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errorPayload = await response.json();
        detail = errorPayload.detail || detail;
      } catch {
        detail = await response.text();
      }
      throw new Error(detail);
    }
    const report = await response.json();
    setTimeout(() => {
      stopLoading();
      renderReport(report);
    }, 900);
  } catch (error) {
    stopLoading();
    statusLabel.textContent = "модель легла лицом в протокол";
    loadingMessage.textContent = String(error.message || error).slice(0, 180);
    console.error(error);
  }
});

document.querySelector("#downloadButton").addEventListener("click", () => {
  downloadReportImage().catch((error) => {
    statusLabel.textContent = "не удалось скачать карточку";
    console.error(error);
  });
});

document.querySelector("#againButton").addEventListener("click", () => {
  resultPanel.hidden = true;
  lastReport = null;
  showStep(1);
  statusLabel.textContent = "новое дело открыто";
});

form.addEventListener("input", saveAuraSession);

if (!restoreAuraSession()) {
  showStep(0);
}
