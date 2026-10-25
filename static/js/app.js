document.addEventListener('DOMContentLoaded', () => {
    const scheduleContainer = document.getElementById('scheduleContainer');
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const noResults = document.getElementById('noResults');

    let eventsData = [];

    // Fetch schedule data from backend API
    const fetchSchedule = async () => {
        try {
            const response = await fetch('/api/schedule');
            eventsData = await response.json();
            renderSchedule(eventsData);
        } catch (error) {
            console.error("Failed to fetch schedule:", error);
            scheduleContainer.innerHTML = "<p>Error loading schedule. Please try again later.</p>";
        }
    };

    // Render HTML for events
    const renderSchedule = (events) => {
        scheduleContainer.innerHTML = '';
        
        if (events.length === 0) {
            noResults.classList.remove('hidden');
            return;
        } else {
            noResults.classList.add('hidden');
        }

        events.forEach(event => {
            const cardElement = document.createElement('div');
            cardElement.className = `event-card ${event.type === 'break' ? 'break-type' : ''}`;
            
            // Format category class dynamically based on id if exists
            const catClass = event.category ? `cat-${event.category}` : '';
            
            // Build Speakers HTML
            let speakersHTML = '';
            if (event.speakers && event.speakers.length > 0) {
                const speakersList = event.speakers.map(speaker => {
                    const initials = `${speaker.first_name[0]}${speaker.last_name[0]}`;
                    const fullName = `${speaker.first_name} ${speaker.last_name}`;
                    return `
                        <div class="speaker">
                            <div class="speaker-avatar">${initials}</div>
                            <div class="speaker-info">
                                <a href="${speaker.linkedin}" target="_blank" rel="noopener noreferrer">${fullName}</a>
                            </div>
                        </div>
                    `;
                }).join('');
                speakersHTML = `<div class="event-speakers">${speakersList}</div>`;
            }

            // Build badge HTML
            let badgeHTML = '';
            if (event.category_name && event.type !== 'break') {
                badgeHTML = `<div class="event-category-badge ${catClass}">${event.category_name}</div>`;
            }

            cardElement.innerHTML = `
                <div class="event-time">${event.time}</div>
                <div class="event-content">
                    ${badgeHTML}
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-desc">${event.description}</p>
                    ${speakersHTML}
                </div>
            `;
            
            scheduleContainer.appendChild(cardElement);
        });
    };

    // Filter Logic
    const filterEvents = () => {
        const query = searchInput.value.toLowerCase();
        const category = categoryFilter.value;

        const filtered = eventsData.filter(event => {
            // Keep breaks if there is no filter applied, otherwise hide them unless "all" category and no search term
            if (event.type === 'break') {
                return category === 'all' && query === '';
            }

            const matchCategory = category === 'all' || event.category === category;
            
            const matchTitle = event.title.toLowerCase().includes(query);
            
            // Match speaker names
            const matchSpeaker = event.speakers && event.speakers.some(speaker => {
                const fullName = `${speaker.first_name} ${speaker.last_name}`.toLowerCase();
                return fullName.includes(query);
            });

            return matchCategory && (matchTitle || matchSpeaker);
        });

        // Insert breaks back in place chronologically if we have a pure 'all' and no query. 
        // We already handled this cleanly in the logic above though.
        
        renderSchedule(filtered);
    };

    // Event Listeners
    searchInput.addEventListener('input', filterEvents);
    categoryFilter.addEventListener('change', filterEvents);

    // Initial load
    fetchSchedule();
});
