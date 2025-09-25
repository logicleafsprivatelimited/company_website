// This single script will handle both the index.html and contact.html forms.

// We wrap our code in a DOMContentLoaded event listener.
// This ensures the script only runs after the entire HTML page has been loaded.
document.addEventListener("DOMContentLoaded", () => {
    
    // Find any form on the page with the id "contact-form".
    const contactForm = document.getElementById("contact-form");

    // If a form with that ID exists on the current page, attach our submission logic to it.
    if (contactForm) {
        contactForm.addEventListener("submit", async (e) => {
            // 1. Prevent the default browser action of reloading the page on submit.
            e.preventDefault();

            const form = e.target;
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;

            // 2. Give the user visual feedback that something is happening.
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            try {
                // 3. Send the form data to our FastAPI backend using the fetch API.
                // ✅ FIXED: The URL is now corrected to 127.0.0.1
                const response = await fetch("http://127.0.0.1:8000/submit-form", {
                    method: "POST",
                    body: formData, // FormData automatically sets the correct headers.
                });

                // 4. Handle the response from the server.
                if (response.ok) {
                    // If the server responds with a success status (like 200 OK)...
                    alert("Thank you! Your message has been sent successfully.");
                    form.reset(); // Clear the form fields.
                } else {
                    // If the server responds with an error status (like 500)...
                    const errorResult = await response.json();
                    console.error("Server Error:", errorResult.detail);
                    alert(`Submission failed: ${errorResult.detail}`);
                }
            } catch (error) {
                // 5. Handle network errors (e.g., if the server is not running).
                console.error("Network or Fetch Error:", error);
                alert("Sorry, we couldn't connect to the server. Please make sure it's running and try again.");
            } finally {
                // 6. Always re-enable the button, whether the submission succeeded or failed.
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }
});

