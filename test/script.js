const dropContainer = document.getElementById("drop_file_zone")
const fileInput = document.getElementById("files")
const swapButton = document.getElementById("swapping_block")

const changeText = (element, text) => {
    element.fadeOut(() => {
        element.html(text)
        element.fadeIn()
    })
}

dropContainer.onclick = () => {
    fileInput.click()
}

dropContainer.ondragover = event => {
    event.preventDefault()
}

dropContainer.addEventListener("dragenter", () => {
    dropContainer.style.backgroundColor = 'white'
    document.querySelector(".img-fluid").style['-webkit-transform'] = "rotate(15deg)"
    document.querySelector(".img-fluid").style['transform'] = "rotate(15deg)"
}, false);

dropContainer.addEventListener("dragleave", () => {
    dropContainer.style.backgroundColor = '#F6F6F6'
    document.querySelector(".img-fluid").style['-webkit-transform'] = "rotate(0)"
    document.querySelector(".img-fluid").style['transform'] = "rotate(0)"
}, false);

dropContainer.ondrop = event => {
    if (event.dataTransfer.files?.length) {
        fileInput.files = event.dataTransfer.files;
        alert('Successfully uploaded')
    }

    event.preventDefault()
}

fileInput.onchange = () => {
    if (fileInput.files?.length) {
        alert('Successfully uploaded')
    }
}

swapButton.onclick = () => {
    const convertFrom = $('#convert_from')
    const convertTo = $('#convert_to')
    const swapping = {"SESSION": "TDATA", "TDATA": "SESSION"}

    changeText(convertFrom, swapping[convertFrom.text()])
    changeText(convertTo, swapping[convertTo.text()])

    setTimeout(() => {
        document.getElementById('selected_convert_from').value = convertFrom.text()
    }, 500)
}

document.getElementById("start_form").onclick = async event => {
    if (!fileInput.files?.length) {
        alert('It look like you forgot to add files')
        event.preventDefault()
        return
    }

    document.querySelector("#drop_file_zone > div > img").outerHTML = `
        <div class="stage" style="height: 170px;">
            <div class="dot-windmill"></div>
        </div>
    `

    const data = new FormData();

    [...fileInput.files].forEach(file => data.append('files[]', file, file.name))
    data.append("selected_convert_from", $('#convert_from').text())

    await fetch('http://localhost:8080/convert', {
        method: 'POST',
        headers: { "rompegram_key": rompegramKey, "uuid": userUUID},
        body: data
    }).then(async response => await response.blob()).then(async data => {
        const oldOnClick = document.getElementById("start_form").onclick

        document.getElementById("start_form").textContent = "Save"
        document.getElementById("start_form").onclick = async () => {
            const fileHandle = await window.showSaveFilePicker({
                suggestedName: `ConvertedAccounts.zip`,
                multiple: true,
                types: [{
                    description: 'Zip file', 
                    accept: { 'application/zip': ['.zip'] },
                }],
                excludeAcceptAllOption: true
            })
            
            const writableStream = await fileHandle.createWritable()
    
            await writableStream.write(data)
            await writableStream.close()

            document.getElementById("start_form").textContent = "Start"
            document.getElementById("start_form").onclick = oldOnClick
        }
    
    }).catch(error => {
        alert('Field to convert')
        console.error(error)

    }).finally(() => {
        document.querySelector("#drop_file_zone > div > div").outerHTML = `
            <img src="drop_files.png" style="width: 100px;padding-bottom: 10px;" class="img-fluid">
        `
    })
}
