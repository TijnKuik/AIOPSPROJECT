const retrainModelButton = document.getElementById("retrain_m");
const outputValueLabel = document.getElementById("output_value");

const addInput1 = document.getElementById("add_v1");
const addInput2 = document.getElementById("add_v2");
const addButton = document.getElementById("add_button");

function sendAdditionData(dataObj){
    fetch("http://localhost:8000/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(dataObj)
      });

};


addButton.addEventListener("click", async () =>{
    const add_v1 = Number(addInput1.value);
    const add_v2 = Number(addInput2.value);

    const addData = {
        v1: add_v1,
        v2:add_v2
    };

    const result = await sendAdditionData(addData);
    console.log(result);
});


retrainModelButton.addEventListener("click", () =>{
    outputValueLabel.textContent = Number(addInput1.value);
});
