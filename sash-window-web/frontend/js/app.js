import { calculateProject, exportProject, downloadUrl } from "./api.js";
import { renderWindow, clearPreview } from "./renderer.js";
import { PreviewViewer } from "./viewer.js";

const form = document.getElementById("window-form");
const previewSvg = document.getElementById("preview-canvas");
const viewerContainer = document.getElementById("viewer");
const viewerEmpty = document.getElementById("viewer-empty");
const resultsContainer = document.getElementById("results");
const exportsContainer = document.getElementById("exports");
const toast = document.getElementById("toast");
const zoomInBtn = document.getElementById("zoom-in");
const zoomOutBtn = document.getElementById("zoom-out");
const zoomResetBtn = document.getElementById("zoom-reset");
const tabButtons = document.querySelectorAll(".tab-button");
const tabPanels = {
  graphics: document.getElementById("panel-graphics"),
  results: document.getElementById("panel-results"),
  exports: document.getElementById("panel-exports"),
};

const STORAGE_KEY = "sash-window-config";
const viewer = new PreviewViewer(viewerContainer, previewSvg);
viewer.init();

const state = {
  lastPayload: null,
  lastResponse: null,
  downloadsList: null,
};

function showToast(message, type = "info") {
  toast.textContent = message;
  toast.classList.remove("hidden");
  toast.classList.add("toast-show");
  toast.dataset.type = type;
  setTimeout(() => {
    toast.classList.add("hidden");
    toast.classList.remove("toast-show");
  }, 3000);
}

function setActiveTab(target) {
  tabButtons.forEach((button) => {
    const isActive = button.dataset.target === target;
    button.classList.toggle("active", isActive);
  });
  Object.entries(tabPanels).forEach(([key, panel]) => {
    panel.classList.toggle("hidden", key !== target);
  });
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveTab(button.dataset.target));
});

zoomInBtn.addEventListener("click", () => viewer.zoomIn());
zoomOutBtn.addEventListener("click", () => viewer.zoomOut());
zoomResetBtn.addEventListener("click", () => viewer.reset());

function persistForm() {
  const payload = {};
  Array.from(form.elements).forEach((element) => {
    if (!element.name || element.type === "submit") return;
    if (element.type === "checkbox") {
      payload[element.name] = element.checked;
    } else {
      payload[element.name] = element.value;
    }
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function restoreForm() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    const payload = JSON.parse(raw);
    Object.entries(payload).forEach(([name, value]) => {
      const element = form.elements[name];
      if (!element) return;
      if (element.type === "checkbox") {
        element.checked = Boolean(value);
      } else {
        element.value = value;
      }
    });
  } catch (error) {
    console.warn("Unable to restore form state", error);
  }
}

restoreForm();

function buildPayload() {
  const data = new FormData(form);
  const toNumber = (name) => Number(data.get(name));
  const toInt = (name) => parseInt(data.get(name), 10);
  const projectName = data.get("projectName").trim();
  const clientName = data.get("clientName").trim();
  const windowName = data.get("windowName").trim();

  const windowConfig = {
    name: windowName,
    frame_width: toNumber("frameWidth"),
    frame_height: toNumber("frameHeight"),
    top_sash_height: toNumber("topSashHeight"),
    bottom_sash_height: toNumber("bottomSashHeight"),
    paint_color: data.get("paintColor").trim(),
    hardware_finish: data.get("hardwareFinish").trim(),
    trickle_vent: data.get("trickleVent").trim(),
    sash_catches: data.get("sashCatches").trim(),
    cill_extension: toInt("cillExtension"),
    glass_type: data.get("glassType").trim(),
    glass_frosted: form.elements["glassFrosted"].checked,
    glass_toughened: form.elements["glassToughened"].checked,
    spacer_color: data.get("spacerColor").trim(),
    glass_pcs: toInt("glassPcs"),
    bars_layout: data.get("barsLayout").trim(),
    bars_vertical: toInt("barsVertical"),
    bars_horizontal: toInt("barsHorizontal"),
  };

  const woodType = data.get("woodType");
  if (woodType) {
    windowConfig.wood_type = woodType.trim();
  }

  return {
    project: {
      name: projectName,
      client_name: clientName,
    },
    windows: [windowConfig],
  };
}

function formatNumber(value, digits = 1) {
  if (Number.isNaN(Number(value))) return "-";
  return Number(value).toFixed(digits);
}

function renderMaterials(materials = []) {
  if (!materials.length) return "";
  const rows = materials
    .map(
      (item) => `
        <tr>
          <td class="px-3 py-2">${item.material_type}</td>
          <td class="px-3 py-2">${item.section}</td>
          <td class="px-3 py-2 text-right">${formatNumber(item.length, 2)} mm</td>
          <td class="px-3 py-2 text-right">${item.qty}</td>
          <td class="px-3 py-2">${item.wood_type}</td>
        </tr>
      `,
    )
    .join("");

  return `
    <div>
      <h4 class="text-sm font-semibold text-slate-700 mb-2">Lista cięć</h4>
      <div class="overflow-hidden rounded-lg border border-slate-200">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-slate-500 uppercase tracking-wide text-xs">
            <tr>
              <th class="px-3 py-2 text-left">Element</th>
              <th class="px-3 py-2 text-left">Sekcja</th>
              <th class="px-3 py-2 text-right">Długość</th>
              <th class="px-3 py-2 text-right">Ilość</th>
              <th class="px-3 py-2 text-left">Drewno</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">${rows}</tbody>
        </table>
      </div>
    </div>
  `;
}

function renderWindowSummary(windowData) {
  const frame = windowData.export.window.frame;
  const sashTop = windowData.export.window.sash_top;
  const sashBottom = windowData.export.window.sash_bottom;
  const glass = windowData.export.glass;
  const bars = windowData.export.bars;
  const verticalSpacing = Array.isArray(bars.spacing_vertical) && bars.spacing_vertical.length
    ? bars.spacing_vertical.map((value) => formatNumber(value, 2)).join(", ")
    : "-";
  const horizontalSpacing = Array.isArray(bars.spacing_horizontal) && bars.spacing_horizontal.length
    ? bars.spacing_horizontal.map((value) => formatNumber(value, 2)).join(", ")
    : "-";
  const hardware = windowData.export.hardware;
  const totals = windowData.export.totals;

  return `
    <article class="border border-slate-200 rounded-lg p-4 bg-slate-50">
      <header class="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h3 class="text-lg font-semibold text-slate-800">${windowData.name}</h3>
          <p class="text-xs uppercase tracking-wide text-slate-500">ID: ${windowData.id}</p>
        </div>
        <span class="rounded-full bg-blue-50 text-blue-600 px-3 py-1 text-xs font-semibold">${windowData.wood_type || "Sapele"}</span>
      </header>
      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <section class="space-y-2 text-sm">
          <h4 class="font-semibold text-slate-700">Rama & skrzydła</h4>
          <ul class="space-y-1 text-slate-600">
            <li>Rama: ${formatNumber(frame.width)} × ${formatNumber(frame.height)} mm</li>
            <li>Górne skrzydło: ${formatNumber(sashTop.width)} × ${formatNumber(sashTop.height)} mm</li>
            <li>Dolne skrzydło: ${formatNumber(sashBottom.width)} × ${formatNumber(sashBottom.height)} mm</li>
          </ul>
        </section>
        <section class="space-y-2 text-sm">
          <h4 class="font-semibold text-slate-700">Szklenie & szczebliny</h4>
          <ul class="space-y-1 text-slate-600">
            <li>Szkło: ${glass.type}, ${formatNumber(glass.width)} × ${formatNumber(glass.height)} mm (${glass.pcs} szt.)</li>
            <li>Szprosy: ${bars.layout_type} (V: ${bars.vertical_bars}, H: ${bars.horizontal_bars})</li>
            <li>Odstępy pionowe: ${verticalSpacing}</li>
            <li>Odstępy poziome: ${horizontalSpacing}</li>
          </ul>
        </section>
        <section class="space-y-2 text-sm">
          <h4 class="font-semibold text-slate-700">Wykończenie</h4>
          <ul class="space-y-1 text-slate-600">
            <li>Kolor lakieru: ${hardware.paint_color}</li>
            <li>Okucia: ${hardware.hardware_finish}</li>
            <li>Nawiewnik: ${hardware.trickle_vent}</li>
            <li>Zatrzaski: ${hardware.sash_catches}</li>
          </ul>
        </section>
        <section class="space-y-2 text-sm">
          <h4 class="font-semibold text-slate-700">Podsumowanie</h4>
          <ul class="space-y-1 text-slate-600">
            <li>Drewno łącznie: ${formatNumber(totals.timber_length, 2)} mm</li>
            <li>Powierzchnia szkła: ${formatNumber(totals.glass_area, 3)} m²</li>
          </ul>
        </section>
      </div>
      <div class="mt-4">${renderMaterials(windowData.export.materials)}</div>
    </article>
  `;
}

function updateResults(response) {
  const markup = response.windows.map(renderWindowSummary).join("");
  resultsContainer.innerHTML = markup;
}

function createExportButton(format, label) {
  const button = document.createElement("button");
  button.type = "button";
  button.dataset.format = format;
  button.className = "inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition disabled:opacity-60 disabled:cursor-not-allowed";
  button.textContent = label;
  return button;
}

function updateExports(response) {
  exportsContainer.innerHTML = "";
  const info = document.createElement("p");
  info.className = "text-sm text-slate-600";
  info.textContent = "Wygeneruj profesjonalne eksporty z ostatnich obliczeń.";

  const buttonsWrapper = document.createElement("div");
  buttonsWrapper.className = "flex flex-wrap gap-3 mt-3";

  const formats = [
    { format: "pdf", label: "Raport PDF" },
    { format: "excel", label: "Excel (XLSX)" },
    { format: "dxf", label: "DXF (CAD)" },
    { format: "svg", label: "SVG" },
    { format: "png", label: "PNG" },
  ];

  formats.forEach(({ format, label }) => {
    const button = createExportButton(format, label);
    button.addEventListener("click", () => handleExport(button, format));
    buttonsWrapper.appendChild(button);
  });

  const downloadsList = document.createElement("div");
  downloadsList.id = "download-list";
  downloadsList.className = "mt-4 space-y-2";

  exportsContainer.append(info, buttonsWrapper, downloadsList);
  state.downloadsList = downloadsList;
}

function appendDownload(result, format) {
  if (!state.downloadsList) return;
  const item = document.createElement("div");
  item.className = "flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm";
  const link = document.createElement("a");
  link.href = downloadUrl(result.file_id);
  link.textContent = `${result.filename} (${(result.size / 1024).toFixed(1)} KB)`;
  link.className = "text-blue-600 hover:underline";
  link.setAttribute("download", result.filename);
  link.target = "_blank";

  const badge = document.createElement("span");
  badge.className = "rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase text-slate-500";
  badge.textContent = format.toUpperCase();

  item.append(link, badge);
  state.downloadsList.prepend(item);
}

async function handleExport(button, format) {
  if (!state.lastPayload) {
    showToast("Najpierw przelicz projekt", "warning");
    return;
  }

  button.disabled = true;
  const originalLabel = button.textContent;
  button.textContent = "Generowanie...";

  try {
    const result = await exportProject(format, state.lastPayload);
    appendDownload(result, format);
    showToast(`Eksport ${format.toUpperCase()} gotowy.`);
  } catch (error) {
    showToast(error.message || "Nie udało się wygenerować eksportu", "error");
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

function updatePreview(response) {
  if (!response.windows.length) {
    clearPreview(previewSvg);
    viewerEmpty.classList.remove("hidden");
    return;
  }
  const firstWindow = response.windows[0];
  renderWindow(previewSvg, firstWindow.renderer);
  viewerEmpty.classList.add("hidden");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    const payload = buildPayload();
    state.lastPayload = payload;
    persistForm();

    const response = await calculateProject(payload);
    state.lastResponse = response;

    updatePreview(response);
    updateResults(response);
    updateExports(response);
    setActiveTab("graphics");
    showToast("Obliczenia zakończone powodzeniem.");
  } catch (error) {
    showToast(error.message || "Wystąpił błąd podczas obliczeń", "error");
  }
});

// Initialise view
setActiveTab("graphics");
