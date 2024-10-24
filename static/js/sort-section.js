document.addEventListener('DOMContentLoaded', function() {
    var sortable = Sortable.create(document.getElementById('section-list'), {
        animation: 150,
        onEnd: function (evt) {
            console.log("Section order changed. Click 'Update Position' to save changes.");
        }
    });

    var updateButton = document.getElementById('update-position-btn');
    if (updateButton) {
        updateButton.addEventListener('click', function() {
            console.log("Button clicked");

            // Explicitly exclude the "No sections available" element by checking for section-query class
            const sections = document.querySelectorAll('li.section-query[id^="section-"]');
            console.log("Found valid sections:", sections.length);

            let order = [];
            
            sections.forEach((section) => {
                // Log the current section element for debugging
                console.log("Processing section:", section.outerHTML);
                
                // Get the section ID and position
                let sectionId = section.id.replace('section-', '');
                let position = section.getAttribute('data-position');
                
                console.log("Extracted data:", {
                    sectionId: sectionId,
                    position: position
                });

                if (sectionId && position && !isNaN(parseInt(sectionId)) && !isNaN(parseInt(position))) {
                    order.push({
                        id: parseInt(sectionId),
                        position: parseInt(position)
                    });
                    console.log("Added to order:", {
                        id: parseInt(sectionId),
                        position: parseInt(position)
                    });
                }
            });

            console.log("Final order array:", order);
            
            const projectId = document.getElementById("project-id").value;

            console.log("porjectid:", projectId)
            
            if (order.length > 0) {
                updateSectionOrder(order, projectId);
            } else {
                console.log("No valid sections to update.");
            }
        });
    } else {
        console.error("Update button not found in the DOM.");
    }
});

function updateSectionOrder(order, projectId) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/project/${projectId}/update-section-order/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            order: order,
            project_id: projectId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Section order updated successfully");
            showSuccessMessage("Section order updated successfully");
        } else {
            console.error("Error:", data.error);
            showErrorMessage("Failed to update section order");
        }
    })
    .catch(error => {
        console.error("An error occurred:", error);
        showErrorMessage("An error occurred while updating section order");
    });
}

function showSuccessMessage(message) {
    alert(message);
}

function showErrorMessage(message) {
    alert(message);
}