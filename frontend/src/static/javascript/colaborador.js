//Im tired, this is self-explanatory I think (what it does I mean)
function fetchColaboradorName() {
    var colaboradorId = document.getElementById('colaborador_id').value;
    
    if (colaboradorId > 0) {
        fetch('/get_colaborador_name/' + colaboradorId)
        .then(response => response.text())
        .then(data => {
            document.getElementById('colaborador_name').innerText = "Nombre del Colaborador: " + data;
        })
        .catch(error => {
            document.getElementById('colaborador_name').innerText = "Nombre del Colaborador: Does not exist";
        });
    } else {
        document.getElementById('colaborador_name').innerText = "Nombre del Colaborador: Does not exist";
    }
}

//CAN ADD MORE FUNCTIONS BELOW TO FETCH OTHER THINGS FROM COLABORADOR SPECIFICALLY (to keep order)
//https://stackoverflow.com/questions/2435525/best-practice-access-form-elements-by-html-id-or-name-attribute
//https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
//Solution I found to do the silly thing with the ids in add_contrato page.