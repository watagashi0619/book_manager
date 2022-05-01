<template>
  <div style="display: block">
    <div>{{ result_list }}</div>
    <br />
    <br />
    <div id="cameraArea"></div>
  </div>
</template>

<script>
// import Quagga from "quagga";
import Quagga from "@ericblade/quagga2";

let regex = /978\d{10}/;

export default {
  name: "BarcodeScanner",
  data() {
    return {
      result_list: [],
      format: "",
    };
  },
  mounted() {
    const config = {
      inputStream: {
        name: "Live",
        type: "LiveStream",
        target: document.querySelector("#cameraArea"),
        constraints: {
          width: { min: 640 },
          height: { min: 480 },
          facingMode: "environment",
          aspectRatio: { min: 1, max: 2 },
        },
      },
      locator: {
        patchSize: "medium",
        halfSample: true,
      },
      numOfWorkers: 2,
      frequency: 10,
      decoder: { readers: ["ean_reader", "ean_8_reader"] },
      locate: true,
    };
    Quagga.init(config, function (err) {
      if (err) {
        return console.error(err);
      }
      Quagga.start();
    });
    Quagga.onDetected(this.onDetected);
    Quagga.onProcessed(this.onProcessed);
  },
  destroyed() {
    if (this.onDetected) Quagga.offDetected(this.onDetected);
    if (this.onProcessed) Quagga.offProcessed(this.offProcessed);
    Quagga.stop();
  },
  watch: {
    onDetected: function (oldValue, newValue) {
      if (oldValue) Quagga.offDetected(oldValue);
      if (newValue) Quagga.onDetected(newValue);
    },
    onProcessed: function (oldValue, newValue) {
      if (oldValue) Quagga.offProcessed(oldValue);
      if (newValue) Quagga.onProcessed(newValue);
    },
  },
  methods: {
    onProcessed(result) {
      let drawingCtx = Quagga.canvas.ctx.overlay,
        drawingCanvas = Quagga.canvas.dom.overlay;

      if (result) {
        if (result.boxes) {
          drawingCtx.clearRect(
            0,
            0,
            parseInt(drawingCanvas.getAttribute("width")),
            parseInt(drawingCanvas.getAttribute("height"))
          );
          result.boxes
            .filter(function (box) {
              return box !== result.box;
            })
            .forEach(function (box) {
              Quagga.ImageDebug.drawPath(box, { x: 0, y: 1 }, drawingCtx, {
                color: "green",
                lineWidth: 2,
              });
            });
        }
        if (result.box && regex.test(result.codeResult.code)) {
          Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, drawingCtx, {
            color: "#00F",
            lineWidth: 2,
          });
        }
        if (result.codeResult && regex.test(result.codeResult.code)) {
          Quagga.ImageDebug.drawPath(
            result.line,
            { x: "x", y: "y" },
            drawingCtx,
            { color: "red", lineWidth: 3 }
          );
        }
      }
    },
    onDetected(result) {
      if (regex.test(result.codeResult.code)) {
        if (this.result_list.indexOf(result.codeResult.code) == -1) {
          this.result_list.push(result.codeResult.code);
        }
        this.format = result.codeResult.format;
      }
    },
  },
};
</script>

<style>
#cameraArea {
  position: relative;
}
#cameraArea video,
#cameraArea canvas {
  position: absolute;
  left: 0;
  top: 0;
}
</style>


