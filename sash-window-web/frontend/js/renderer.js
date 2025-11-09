const SVG_NS = "http://www.w3.org/2000/svg";

function createElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    element.setAttribute(key, value);
  });
  return element;
}

function computeCanvas(bounds) {
  const padding = 80;
  if (!bounds) {
    return {
      padding,
      width: 1200,
      height: 1600,
      viewWidth: 1200 + padding * 2,
      viewHeight: 1600 + padding * 2,
      minX: 0,
      minY: 0,
    };
  }

  const width = bounds.max.x - bounds.min.x;
  const height = bounds.max.y - bounds.min.y;
  const safeWidth = Math.max(width, 200);
  const safeHeight = Math.max(height, 200);

  return {
    padding,
    width: safeWidth,
    height: safeHeight,
    viewWidth: safeWidth + padding * 2,
    viewHeight: safeHeight + padding * 2,
    minX: bounds.min.x,
    minY: bounds.min.y,
  };
}

function transformY(y, canvas) {
  return canvas.height - (y - canvas.minY) + canvas.padding;
}

function transformX(x, canvas) {
  return x - canvas.minX + canvas.padding;
}

export function clearPreview(svgElement) {
  while (svgElement.firstChild) {
    svgElement.removeChild(svgElement.firstChild);
  }
}

export function renderWindow(svgElement, rendererPayload) {
  clearPreview(svgElement);

  if (!rendererPayload || !rendererPayload.summary) {
    svgElement.setAttribute("viewBox", "0 0 1200 1600");
    return;
  }

  const bounds = rendererPayload.summary.bounds;
  const canvas = computeCanvas(bounds);
  svgElement.setAttribute("viewBox", `0 0 ${canvas.viewWidth} ${canvas.viewHeight}`);
  svgElement.setAttribute("width", canvas.viewWidth);
  svgElement.setAttribute("height", canvas.viewHeight);

  const layerGroup = createElement("g", { transform: `matrix(1 0 0 1 0 0)` });
  svgElement.appendChild(layerGroup);

  const layers = new Map();
  const getLayerGroup = (layer) => {
    if (!layer) return layerGroup;
    if (!layers.has(layer)) {
      const group = createElement("g", { id: `layer-${layer.toLowerCase()}` });
      layers.set(layer, group);
      layerGroup.appendChild(group);
    }
    return layers.get(layer);
  };

  const toStrokeDasharray = (linestyle) => {
    if (linestyle === "dashed") return "6 4";
    if (linestyle === "dotted") return "2 2";
    return "";
  };

  // Draw rectangles
  rendererPayload.rectangles.forEach((rect) => {
    const group = getLayerGroup(rect.layer);
    const attrs = {
      x: transformX(rect.x, canvas),
      y: transformY(rect.y + rect.height, canvas),
      width: rect.width,
      height: rect.height,
      fill: rect.fill ? rect.color : "none",
      stroke: rect.color,
      "stroke-width": rect.linewidth ?? 0.6,
      "fill-opacity": rect.alpha ?? 1,
    };
    group.appendChild(createElement("rect", attrs));
  });

  // Draw lines
  rendererPayload.lines.forEach((line) => {
    const group = getLayerGroup(line.layer);
    const attrs = {
      x1: transformX(line.x1, canvas),
      y1: transformY(line.y1, canvas),
      x2: transformX(line.x2, canvas),
      y2: transformY(line.y2, canvas),
      stroke: line.color,
      "stroke-width": line.linewidth ?? 0.5,
    };
    const dash = toStrokeDasharray(line.linestyle);
    if (dash) attrs["stroke-dasharray"] = dash;
    group.appendChild(createElement("line", attrs));
  });

  // Draw dimension helpers
  rendererPayload.dimensions.forEach((dimension) => {
    const group = getLayerGroup(dimension.layer);
    const attrs = {
      x1: transformX(dimension.x1, canvas),
      y1: transformY(dimension.y1 + dimension.offset, canvas),
      x2: transformX(dimension.x2, canvas),
      y2: transformY(dimension.y2 + dimension.offset, canvas),
      stroke: dimension.color,
      "stroke-width": 0.7,
      "marker-start": "url(#arrow-start)",
      "marker-end": "url(#arrow-end)",
    };
    group.appendChild(createElement("line", attrs));
  });

  // Draw texts
  rendererPayload.texts.forEach((text) => {
    const group = getLayerGroup(text.layer);
    const attrs = {
      x: transformX(text.x, canvas),
      y: transformY(text.y, canvas),
      fill: text.color,
      "font-size": text.size ?? 3,
      "text-anchor": text.halign === "left" ? "start" : text.halign === "right" ? "end" : "middle",
      "dominant-baseline": text.valign === "top" ? "hanging" : text.valign === "bottom" ? "baseline" : "middle",
    };
    const textElement = createElement("text", attrs);
    if (text.rotation) {
      textElement.setAttribute("transform", `rotate(${text.rotation}, ${attrs.x}, ${attrs.y})`);
    }
    textElement.textContent = text.text;
    group.appendChild(textElement);
  });

  // Dimension arrow marker definitions
  const defs = createElement("defs");
  const markerStart = createElement("marker", {
    id: "arrow-start",
    markerWidth: 6,
    markerHeight: 6,
    refX: 3,
    refY: 3,
    orient: "auto",
    markerUnits: "strokeWidth",
  });
  markerStart.appendChild(createElement("path", {
    d: "M3,3 L6,6 L6,0 Z",
    fill: "#FF6B6B",
  }));
  const markerEnd = createElement("marker", {
    id: "arrow-end",
    markerWidth: 6,
    markerHeight: 6,
    refX: 3,
    refY: 3,
    orient: "auto",
    markerUnits: "strokeWidth",
  });
  markerEnd.appendChild(createElement("path", {
    d: "M0,0 L0,6 L3,3 Z",
    fill: "#FF6B6B",
  }));
  defs.appendChild(markerStart);
  defs.appendChild(markerEnd);
  svgElement.insertBefore(defs, layerGroup);
}
