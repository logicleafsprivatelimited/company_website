document.addEventListener("DOMContentLoaded", () => {
    // This script now handles ANY form with the id "contact-form"
    const contactForm = document.getElementById("contact-form");

    if (contactForm) {
        contactForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Stop the default form submission

            const form = e.target;
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;

            // Disable button and show "Sending..."
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            try {
                // Submit the form data to Formspree
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData,
                    headers: {
                        'Accept': 'application/json' // Required for Formspree AJAX
                    }
                });

                // Check if Formspree accepted the submission
                if (response.ok) {
                    alert("Thank you! Your message has been sent.");
                    form.reset(); // Clear the form fields
                } else {
                    // Handle errors from Formspree
                    const result = await response.json();
                    if (result.errors) {
                        const message = result.errors.map(err => err.message).join(', ');
                        alert("Submission failed: " + message);
                    } else {
                         alert("Submission failed. Please try again.");
                    }
                }
            } catch (error) {
                // Handle network errors
                console.error("Network or Fetch Error:", error);
                alert("Sorry, we couldn't connect to the server. Please try again later.");
            } finally {
                // Re-enable the button and restore original text
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }
});
