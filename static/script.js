document.addEventListener('DOMContentLoaded', function() {
    const autocompleteInput = document.getElementById('autocomplete');
    const suggestionsDiv = document.getElementById('suggestions');

    autocompleteInput.addEventListener('input', function() {
        const query = this.value;
        
        if (query.length > 0) {
            fetch(\/autocomplete?query=\\)
                .then(response => response.json())
                .then(data => {
                    suggestionsDiv.innerHTML = '';
                    data.forEach(item => {
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'suggestion-item';
                        suggestionItem.textContent = item;
                        suggestionItem.onclick = function() {
                            autocompleteInput.value = item; // Remplir l'input avec le choix
                            suggestionsDiv.innerHTML = ''; // Effacer les suggestions
                        };
                        suggestionsDiv.appendChild(suggestionItem);
                    });
                });
        } else {
            suggestionsDiv.innerHTML = ''; // Effacer les suggestions si l'input est vide
        }
    });
});
