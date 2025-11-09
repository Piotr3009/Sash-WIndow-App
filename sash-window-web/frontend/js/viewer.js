export class PreviewViewer {
  constructor(container, svgElement) {
    this.container = container;
    this.svgElement = svgElement;
    this.panzoom = null;
  }

  init() {
    if (typeof window.Panzoom !== "function") {
      console.warn("Panzoom library is not loaded.");
      return;
    }

    this.panzoom = window.Panzoom(this.svgElement, {
      maxScale: 6,
      minScale: 0.2,
      contain: "outside",
      canvas: true,
      zoomDoubleClickSpeed: 1,
    });

    const parent = this.svgElement.parentElement;
    parent.addEventListener("wheel", (event) => {
      if (!this.panzoom) return;
      event.preventDefault();
      const scale = event.deltaY < 0 ? 1.2 : 0.8;
      this.panzoom.zoomWithWheel(event, { step: scale });
    });
  }

  zoomIn() {
    if (this.panzoom) this.panzoom.zoomIn();
  }

  zoomOut() {
    if (this.panzoom) this.panzoom.zoomOut();
  }

  reset() {
    if (this.panzoom) this.panzoom.reset();
  }
}
