//Im tired, this is self-explanatory I think (what it does I mean)
function fetchEmployeeName() {
    var employeeId = document.getElementById('employee_id').value;
    
    if (employeeId > 0) {
        fetch('/get_employee_name/' + employeeId)
        .then(response => response.text())
        .then(data => {
            document.getElementById('employee_name').innerText = "Employee name: " + data;
        })
        .catch(error => {
            document.getElementById('employee_name').innerText = "Employee name: Does not exist";
        });
    } else {
        document.getElementById('employee_name').innerText = "Employee name: Does not exist";
    }
}

//CAN ADD MORE FUNCTIONS BELOW TO FETCH OTHER THINGS FROM EMPLOYEE SPECIFICALLY (to keep order)
//https://stackoverflow.com/questions/2435525/best-practice-access-form-elements-by-html-id-or-name-attribute
//https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
//Solution I found to do the silly thing with the ids in add_contract page.