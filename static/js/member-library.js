const levelFilter = document.getElementById('levelFilter');
const searchFilter = document.getElementById('searchFilter');
const lessonCards = Array.from(document.querySelectorAll('.lesson-card'));

function applyFilters() {
    const selectedLevel = levelFilter ? levelFilter.value : '';
    const searchTerm = searchFilter ? searchFilter.value.toLowerCase().trim() : '';

    lessonCards.forEach((card) => {
        const cardLevel = card.dataset.level || '';
        const cardTitle = card.dataset.title || '';

        const levelMatches = !selectedLevel || cardLevel === selectedLevel;
        const searchMatches = !searchTerm || cardTitle.includes(searchTerm);

        card.style.display = levelMatches && searchMatches ? '' : 'none';
    });
}

if (levelFilter) {
    levelFilter.addEventListener('change', applyFilters);
}

if (searchFilter) {
    searchFilter.addEventListener('input', applyFilters);
}
