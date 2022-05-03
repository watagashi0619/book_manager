let regex = /978\d{10}/;

let scannedList = [];
let scannedCodeList = [];

const startBtn = document.getElementById("scan-start-btn");
const stopBtn = document.getElementById("scan-stop-btn");

const isbn = document.getElementById("isbn");
const booktitle = document.getElementById("booktitle");
const volume = document.getElementById("volume");
const publisher = document.getElementById("publisher");

const scanArea = document.getElementById("scan_area");

stopBtn.addEventListener("click", () => stopScanner());
startBtn.addEventListener("click", () => startScanner());

const startScanner = () => {
    const config = {
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.querySelector("#cameraArea"),
            constraints: {
                width: {
                    min: 580
                },
                height: {
                    min: 640
                },
                facingMode: "environment",
                //aspectRatio: {
                //    min: 1,
                //    max: 2
                //},
            },
        },
        locator: {
            patchSize: "medium",
            halfSample: true,
        },
        numOfWorkers: 2,
        frequency: 10,
        decoder: {
            readers: ["ean_reader", "ean_8_reader"]
        },
        locate: true,
    };

    Quagga.init(config, function (err) {
        if (err) {
            return console.error(err);
        }
        Quagga.start();
    });

    Quagga.onDetected(_onDetected);
    Quagga.onProcessed(_onProcessed);

    isbn.textContent = "";
    booktitle.textContent = "";
    volume.textContent = "";
    publisher.textContent = "";
}

const stopScanner = () => {
    Quagga.stop();
    Quagga.offProcessed(_onProcessed);
    Quagga.offDetected(_onDetected);

    update();
}

async function update() {
    for (let book of scannedList) {
        console.log(book);
        await axios.post("https://10.0.1.13:8888/update", book).then(res => {
            if (res.data == true) {
                let row = document.createElement("tr");
                Object.keys(book).map(key => {
                    let cell = document.createElement("td");
                    let cellText = document.createTextNode(book[key]);
                    cell.appendChild(
                        cellText);
                    row.appendChild(cell);
                });
                let parentNode = document.getElementById("bookshelf-tbody");
                parentNode.prepend(row);
            }
        })
    }
    scannedList = [];
    scannedCodeList = [];
}

const isValid = isbn => {
    const arrIsbn = isbn
        .toString()
        .split("")
        .map(num => parseInt(num));
    let remainder = 0;
    const checkDigit = arrIsbn.pop();

    arrIsbn.forEach((num, index) => {
        remainder += num * (index % 2 == 0 ? 1 : 3);
    });
    remainder %= 10;
    remainder = remainder == 0 ? 0 : 10 - remainder;

    return checkDigit == remainder;
}

function _onProcessed(result) {
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
                    Quagga.ImageDebug.drawPath(box, {
                        x: 0,
                        y: 1
                    }, drawingCtx, {
                        color: "green",
                        lineWidth: 2,
                    });
                });
        }
        if (result.box && regex.test(result.codeResult.code)) {
            Quagga.ImageDebug.drawPath(result.box, {
                x: 0,
                y: 1
            }, drawingCtx, {
                color: "#00F",
                lineWidth: 2,
            });
        }
        if (result.codeResult && regex.test(result.codeResult.code)) {
            Quagga.ImageDebug.drawPath(
                result.line, {
                    x: "x",
                    y: "y"
                },
                drawingCtx, {
                    color: "red",
                    lineWidth: 3
                }
            );
        }
    }
}

function _onDetected(result) {
    if (isValid(result.codeResult.code) && regex.test(result.codeResult.code)) {
        if (scannedCodeList.indexOf(result.codeResult.code) == -1) {
            axios.get(`https://10.0.1.13:8888/get_bookinfo/${result.codeResult.code}`).then(
                (res) => {
                    isbn.textContent = res.data.isbn;
                    booktitle.textContent = res.data.title;
                    volume.textContent = res.data.volume;
                    publisher.textContent = res.data.publisher;
                    scannedList.push(res.data);
                }
            ).catch((error) => console.log(error));
            scannedCodeList.push(result.codeResult.code);
            console.log(result.codeResult.code);
        }
    }
}