document.addEventListener('DOMContentLoaded', function() {
    var sortable = Sortable.create(document.getElementById('section-list'), {
        animation: 150,
        onEnd: function (evt) {
            console.log("Section order changed. Click 'Update Position' to save changes.");
        }
    });

    // Event listener untuk tombol Update Position
    document.getElementById('update-position-btn').addEventListener('click', function () {
        console.log("Button clicked");
        var order = sortable.toArray().map(id => id.replace('section-', ''));  // Ambil urutan terbaru
        var projectId = document.getElementById('project-id').value; // Ambil project ID
        updateSectionOrder(order, projectId); // Panggil fungsi untuk update posisi
    });
});

function updateSectionOrder(order, projectId) {
    var csrfToken = '{{ csrf_token }}';
    fetch(`/project/${projectId}/update-section-order/`, {  // Perbarui URL dengan project ID
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({order: order, project_id: projectId})  // Kirim urutan baru ke server
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            console.log('Section order updated!');
            location.reload();  // Reload halaman jika perlu, atau atur ulang UI
        }
    })
    .catch(error => console.error('Error:', error));
}
