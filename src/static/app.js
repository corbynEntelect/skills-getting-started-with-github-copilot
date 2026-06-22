document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p class="availability"><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p class="participants-heading"><strong>Participants (${details.participants.length}):</strong></p>
            <ul class="participants-list">
              ${details.participants.length ? details.participants.map(p => `<li><span class="participant-email">${p}</span><button class="delete-participant" data-activity="${encodeURIComponent(name)}" data-email="${encodeURIComponent(p)}" title="Remove participant">✕</button></li>`).join('') : '<li><em>No participants yet</em></li>'}
            </ul>
          </div>
        `;

        // Attach delete handlers for participant remove buttons
        activityCard.querySelectorAll('.delete-participant').forEach((btn) => {
          btn.addEventListener('click', async (e) => {
            const activityEncoded = btn.getAttribute('data-activity');
            const emailEncoded = btn.getAttribute('data-email');
            const activityName = decodeURIComponent(activityEncoded);
            const email = decodeURIComponent(emailEncoded);

            try {
              const res = await fetch(`/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`, {
                method: 'DELETE',
              });

              const data = await res.json();

              if (res.ok) {
                // Remove the participant from the list in the DOM
                const li = btn.closest('li');
                if (li) li.remove();

                // Update participants count and availability text
                const heading = activityCard.querySelector('.participants-heading');
                const list = activityCard.querySelectorAll('.participants-list li');
                const count = Array.from(list).filter(node => !node.querySelector('em')).length;
                heading.innerHTML = `<strong>Participants (${count}):</strong>`;

                const availability = activityCard.querySelector('.availability');
                const newSpotsLeft = details.max_participants - count;
                availability.innerHTML = `<strong>Availability:</strong> ${newSpotsLeft} spots left`;

                // If no participants left, show placeholder
                if (count === 0) {
                  const ul = activityCard.querySelector('.participants-list');
                  ul.innerHTML = '<li><em>No participants yet</em></li>';
                }

                messageDiv.textContent = data.message;
                messageDiv.className = 'success';
                messageDiv.classList.remove('hidden');
                setTimeout(() => messageDiv.classList.add('hidden'), 4000);
              } else {
                messageDiv.textContent = data.detail || 'Failed to remove participant';
                messageDiv.className = 'error';
                messageDiv.classList.remove('hidden');
                setTimeout(() => messageDiv.classList.add('hidden'), 4000);
              }
            } catch (err) {
              console.error('Error removing participant:', err);
              messageDiv.textContent = 'Failed to remove participant. Try again.';
              messageDiv.className = 'error';
              messageDiv.classList.remove('hidden');
              setTimeout(() => messageDiv.classList.add('hidden'), 4000);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
