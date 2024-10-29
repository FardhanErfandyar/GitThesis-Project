document.addEventListener("keydown", async (event) => {
    if (event.ctrlKey && event.key === "s") {
        event.preventDefault();
        event.stopPropagation();

        const textarea = document.activeElement;
        if (textarea.tagName === "TEXTAREA" && textarea.classList.contains("editor-content")) {
            // Retrieve project ID from the hidden input
            const projectID = document.getElementById("project-id").value;
            console.log("Project ID:", projectID);

            // Retrieve section ID from the data attribute of the closest .section-container
            const sectionID = textarea.closest(".section-container")?.getAttribute("data-section-id");
            console.log("Section ID:", sectionID);

            if (!projectID || !sectionID) {
                console.error("Project ID or Section ID is missing.");
                return;
            }

            const updatedContent = textarea.value;
            console.log("Updated content:", updatedContent);

            try {
                const response = await fetch(`/project/${projectID}/update-section/${sectionID}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({ content: updatedContent }),
                });

                console.log("Response status:", response.status);
                if (response.ok) {
                    console.log("Section content successfully updated.");
                } else {
                    console.error("Error updating section content:", response.statusText);
                }
            } catch (error) {
                console.error("Failed to update section:", error);
            }
        }
    }
});
