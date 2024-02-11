let mainTable = document.getElementById('table_body');

function createCurrentBudget(rowId) { 
    let typeLoadElements = document.querySelectorAll(".type_load");
    let budget_sum = 0;
    let cells = mainTable.rows[rowId].cells;
    for (let i = 3; i < typeLoadElements.length * 2 + 3; i++) {
        
        let num = parseInt(cells[i].getElementsByTagName('input')[0].value);
        if (!isNaN(num)) {
            budget_sum += num;
        }
    }
    return budget_sum;
}
    
function setCurrentBudget(rowId, budget_sum) {
    let cells = mainTable.rows[rowId].cells;
    let selectedOptionSubject = cells[1].getElementsByTagName('select')[0].querySelector('option:checked');
    let selectedOptionGroup = cells[2].getElementsByTagName('select')[0].querySelector('option:checked');
    let dataIsPaidValueSubject = selectedOptionSubject.getAttribute('data-is-paid');
    let dataIsPaidValueGroup = selectedOptionGroup.getAttribute('data-is-paid');
    
    if (dataIsPaidValueSubject === 'true' | dataIsPaidValueGroup === 'true') {
        document.getElementById(`budget_0_${rowId+1}`).setAttribute('value', 0);
        document.getElementById(`budget_1_${rowId+1}`).setAttribute('value', budget_sum);
        document.getElementById(`budget_1_${rowId+1}`).value = budget_sum;
    } else {
        document.getElementById(`budget_0_${rowId+1}`).setAttribute('value', budget_sum);
        document.getElementById(`budget_1_${rowId+1}`).setAttribute('value', 0);
        document.getElementById(`budget_0_${rowId+1}`).value = budget_sum;

    }
    document.getElementById(`budget_2_${rowId+1}`).value = budget_sum;
    document.getElementById(`budget_2_${rowId+1}`).setAttribute('value', budget_sum);
    changeResults(dataIsPaidValueSubject, dataIsPaidValueGroup);
}


function changeResults(isPaidSubject, isPaidGroup) {
    let newBudget = 0;
    let newExtraBudget = 0;
    let newTotalBudget = 0;

    if (isPaidSubject === 'true' | isPaidGroup === 'true') {
        let extraBudgetElements = document.querySelectorAll('[id^="budget_1_"]');
        extraBudgetElements.forEach(function(element) {
            newExtraBudget += parseInt(element.value);
        });
        document.getElementById('extra_budget_sum_1').setAttribute('value', newExtraBudget);
        document.getElementById('extra_budget_sum_3').setAttribute('value', newExtraBudget);
    } else {

        let budgetElements = document.querySelectorAll('[id^="budget_0_"]');
        budgetElements.forEach(function(element) {
            newBudget += parseInt(element.value);
        });
        document.getElementById('budget_sum_1').setAttribute('value', newBudget);
        document.getElementById('budget_sum_3').setAttribute('value', newBudget);
    }
    let totalBudgetElements = document.querySelectorAll('[id^="budget_2_"]');
    totalBudgetElements.forEach(function(element) {
        newTotalBudget += parseInt(element.value);
    });
    document.getElementById('budget_result_1').setAttribute('value', newTotalBudget);
    document.getElementById('budget_result_3').setAttribute('value', newTotalBudget);
}

function clearBudget() {
    for (let i = 1; i < 4; i++) {
        document.getElementById(`extra_budget_sum_${i}`).setAttribute('value', 0);
        document.getElementById(`budget_result_${i}`).setAttribute('value', 0);
        document.getElementById(`budget_sum_${i}`).setAttribute('value', 0);
    };
};

function deductFromBudget(budget, extraBudget, totalBudget) {
    document.getElementById('extra_budget_sum_1').setAttribute('value', parseInt(document.getElementById('extra_budget_sum_1').value) - extraBudget);
    document.getElementById('extra_budget_sum_3').setAttribute('value', parseInt(document.getElementById('extra_budget_sum_3').value) - extraBudget);
    document.getElementById('budget_sum_1').setAttribute('value', parseInt(document.getElementById('budget_sum_1').value) - budget);
    document.getElementById('budget_sum_3').setAttribute('value', parseInt(document.getElementById('budget_sum_3').value) - budget);
    document.getElementById('budget_result_1').setAttribute('value', parseInt(document.getElementById('budget_result_1').value) - totalBudget);
    document.getElementById('budget_result_3').setAttribute('value', parseInt(document.getElementById('budget_result_3').value) - totalBudget);

}

export { createCurrentBudget, setCurrentBudget, changeResults, clearBudget, deductFromBudget };