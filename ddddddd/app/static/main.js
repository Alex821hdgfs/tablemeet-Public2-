function initRestaurantsMap(restaurantsData) {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    const map = L.map('map').setView([55.7558, 37.6173], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    restaurantsData.forEach(item => {
        if (item.lat && item.lng) {
            const marker = L.marker([item.lat, item.lng]).addTo(map);
            marker.bindPopup(`
                <b>${item.name}</b><br>
                ${item.address}<br>
                <a href="/restaurant/${item.id}">Открыть</a>
            `);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const guestsSelect = document.getElementById('guests');
    const companionBlock = document.getElementById('companion-block');

    function toggleCompanion() {
        if (!guestsSelect || !companionBlock) return;
        companionBlock.style.display = guestsSelect.value === '1' ? 'block' : 'none';
    }

    if (guestsSelect && companionBlock) {
        toggleCompanion();
        guestsSelect.addEventListener('change', toggleCompanion);
    }
});