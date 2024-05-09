// Select the form element
const form = document.querySelector('form');

// Add event listener for form submission
form.addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent the default form submission
  
  // Perform any necessary validation here
  
  // Serialize the form data
  const formData = new FormData(form);
  
  try {
    // Send a POST request to the server with the form data
    const response = await fetch('/submit_order', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to submit order');
    }
    
    // Redirect to the payment page after successful form submission
    window.location.href = '/payment';
  } catch (error) {
    console.error('Error:', error.message);
    // Handle error here, e.g., display an error message to the user
  }
});
